"""The versioned public tool surface for WordPress projects."""
import time
from benchmark.adapters import Workspace, tool, TOOLS
from benchmark.project import Preview

PROJECT_TOOLS = [t for t in TOOLS if t['function']['name'] != 'read_file'] + [
    tool('read_file', 'Read bounded UTF-8 text. offset is a character offset; limit at most 16000.', ['path', 'offset', 'limit']),
    tool('search_files', 'Search a literal string in project and selected skill files. At most 40 matches.', ['query']),
    tool('preview', 'Sync current source into your WordPress site and return a viewport screenshot and accessible DOM.', []),
    tool('browser', 'Act within the test site. action: navigate, click (CSS selector; editor:: prefix targets the editor canvas), type, key, scroll, viewport. value: text/key/scroll pixels or desktop/mobile. Use empty strings for unused arguments.', ['action', 'target', 'value']),
    tool('public_checks', 'Check activation, native editor block validity, PHP errors and basic accessibility. Final acceptance tests stay hidden.', []),
    tool('submit', 'Freeze the current source and finish generation. No more edits or tool actions are accepted.', []),
]


class ProjectWorkspace(Workspace):
    def __init__(self, task, skill, limits):
        super().__init__(task['initial'], skill['files'] if skill else None)
        self.task, self.limits = task, limits
        self.preview = None
        self.submitted = False
        self.iterations = 0
        self.deadline = time.monotonic() + limits["timeout_seconds"]

    def call(self, name, arguments):
        if self.submitted:
            raise ValueError('Artifact already submitted and frozen')
        if name == 'submit':
            self.submitted = True
            return 'submitted'
        if name == 'search_files':
            query = arguments['query']
            if not isinstance(query, str) or not 1 <= len(query) <= 200:
                raise ValueError('Search query must contain 1–200 characters')
            matches = []
            for prefix, files in [('project/', self.project), ('skill/', self.skill)]:
                for path, content in files.items():
                    for number, line in enumerate(content.splitlines(), 1):
                        if query in line:
                            matches.append({'path': prefix + path, 'line': number, 'text': line[:300]})
                            if len(matches) == 40: return matches
            return matches
        if name in ('preview', 'browser', 'public_checks'):
            if self.preview is None:
                self.preview = Preview(self.task, max(0, self.deadline - time.monotonic()))
            self.iterations += 1
            return self.preview.call(name, arguments, self.project)
        result = super().call(name, arguments)
        if name == 'read_file':
            offset, limit = int(arguments.get('offset', 0)), int(arguments.get('limit', 16000))
            if offset < 0 or not 1 <= limit <= 16000: raise ValueError('Invalid read bounds')
            return {'text': result[offset:offset+limit], 'total_characters': len(result), 'next_offset': offset+limit if offset+limit<len(result) else None}
        return result

    def close(self):
        if self.preview: self.preview.close()
