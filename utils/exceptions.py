class CodeProcessorError(Exception):
    """Base class for exceptions in the code processor."""
    pass

class UnsupportedFileTypeError(CodeProcessorError):
    """Raised when a file type is not supported."""
    pass

class GitRepositoryError(CodeProcessorError):
    """Raised when a file is not in a git repository."""
    pass

class NoRegionTagsError(CodeProcessorError):
    """Raised when no region tags are found in a file."""
    pass

class FirestoreError(Exception):
    """Base class for exceptions in the firestore repository."""
    pass

class RegionTagError(Exception):
    """Base class for exceptions in the region tag extractor."""
    pass

class GitProcessorError(Exception):
    """Base class for exceptions in the git file processor."""
    pass

class CodeEvaluatorError(Exception):
    """Base class for exceptions in the code evaluator."""
    pass