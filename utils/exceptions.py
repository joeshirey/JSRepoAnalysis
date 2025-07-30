class CodeProcessorError(Exception):
    """Base class for exceptions in the code processor."""

    pass


class GitRepositoryError(CodeProcessorError):
    """Raised when a file is not in a git repository."""

    pass


class APIError(CodeProcessorError):
    """Raised when the analysis API call fails."""

    pass


class BigQueryError(Exception):
    """Base class for exceptions in the BigQuery repository."""

    pass


class GitProcessorError(Exception):
    """Base class for exceptions in the git file processor."""

    pass


class CodeEvaluatorError(Exception):
    """Base class for exceptions in the code evaluator."""

    pass
