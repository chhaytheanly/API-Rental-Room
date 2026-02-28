class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @classmethod
    def print(cls, message: str, color: str = OKGREEN):
        print(f"{color}{message}{cls.ENDC}")

    @classmethod
    def success(cls, msg: str): print(f"{cls.OKGREEN}✓ {msg}{cls.ENDC}")
    @classmethod
    def error(cls, msg: str): print(f"{cls.FAIL}✗ {msg}{cls.ENDC}")
    @classmethod
    def info(cls, msg: str): print(f"{cls.OKCYAN}ℹ {msg}{cls.ENDC}")
    @classmethod
    def warning(cls, msg: str): print(f"{cls.WARNING}⚠ {msg}{cls.ENDC}")