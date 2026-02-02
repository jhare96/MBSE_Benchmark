from dataclasses import dataclass
import copy
import glob

@dataclass
class Hunk:
    old_start: int
    old_length: int
    new_start: int
    new_length: int
    lines: list[str]

@dataclass
class FilePatch:
    old_path: str
    new_path: str
    hunks: list[Hunk]


def parse_unified_diff(patch: str) -> list[str]:
    """Parses a unified diff string and returns a list of changes."""
    patches = []
    lines = patch.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line:
            continue

        elif line.startswith('--- ') or line.startswith('+++ '):
            patch, i = parse_patch(lines, i)
            patches.append(patch)
        
    return patches


def parse_patch(lines: list[str], start_idx: int) -> tuple[FilePatch, int]:
    """Parses a single patch from unified diff lines."""
    try:
        i = start_idx
        old_file = lines[i][4:].strip()
        new_file = lines[i+1][4:].strip()
        hunks = []

        i += 2
        while i < len(lines):
            line = lines[i]
            if line.startswith('@@ '):
                hunk, i = parse_hunk(lines, i)
                hunks.append(hunk)
            else:
                i += 1
        
        patch = FilePatch(
            old_path=old_file,
            new_path=new_file,
            hunks=hunks,
        )
        print('patch:', patch, i)
        return patch, i
    except Exception as e:
        print(f"Error parsing patch at line from {lines[start_idx:]}: {e}")
        raise


def parse_hunk(lines, start_idx: int) -> tuple[Hunk, int]:
    """Parses a hunk from unified diff lines."""
    try:
        header = lines[start_idx]
        # Example header: @@ -1,3 +1,4 @@
        print('header:', header)
        header = header.replace('@@', '').strip()
        parts = header.split(' ')
        print('parts:', parts)
        old_info = parts[0].strip('-')  # Remove leading '-'
        new_info = parts[1].strip('+')  # Remove leading '+'

        old_start, old_length = map(int, old_info.split(','))
        new_start, new_length = map(int, new_info.split(','))

        hunk_lines = []
        i = start_idx + 1
        while i < len(lines):
            line = lines[i]
            if line.startswith('@@ '):
                break
            hunk_lines.append(line)
            i += 1

        hunk = Hunk(
            old_start=old_start,
            old_length=old_length,
            new_start=new_start,
            new_length=new_length,
            lines=hunk_lines,
        )
        print('hunk:', hunk, i)
        return hunk, i
    except Exception as e:
        print(f"Error parsing hunk at line from {lines[start_idx:]}: {e}")
        raise

@dataclass
class FileSystem:
    """virtual file system for managing files and applying patches."""
    files: dict[str, str]

    def read_file(self, path: str) -> str:
        return self.files.get(path, f"file {path} not found")

    def list_files(self, path: str) -> list[str]:
        return [file for file in self.files if file.startswith(path)]

    def apply_patch(self, patch: str) -> str:
        try:
            patches = parse_unified_diff(patch)
        except Exception as e:
            return "failed to parse patch with error: " + str(e)
        
        try:
            files_to_update = {}
            for patch in patches:
                content = self.files.get(patch.old_path, "")
                
                if patch.old_path == "/dev/null":
                    files_to_update[patch.new_path] = "\n".join(line[1:] for hunk in patch.hunks for line in hunk.lines if line.startswith('+'))
                    continue
                
                if not content:
                    print(f"File {patch.old_path} not found, skipping patch.")
                    continue

                content_lines = content.splitlines(keepends=True)
                new_content_lines = copy.deepcopy(content_lines)
                for hunk in patch.hunks:
                    j = hunk.new_start
                    for line in hunk.lines:
                        if line.startswith('+'):
                            new_content_lines.insert(j - 1, line[1:])
                            j += 1
                        elif line.startswith('-'):
                            del new_content_lines[j - 1]
                        else:
                            j += 1
                
                files_to_update[patch.new_path] = ''.join(new_content_lines)

            self.files.update(files_to_update)
            return "patch applied successfully"
        except Exception as e:
            return "failed to apply patch with error: " + str(e)
    
    def snapshot(self) -> dict[str, str]:
        return copy.deepcopy(self.files)


def load_virtual_filesystem(task_dir: str) -> FileSystem:
    files = glob.glob(f"{task_dir}/files/*", recursive=True)
    fs = FileSystem(files={file.replace(f"{task_dir}/files/", ""): open(file, 'r').read() for file in files})
    return fs

