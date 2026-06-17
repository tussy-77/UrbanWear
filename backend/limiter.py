from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# storage_uri="memory://" works for single-process dev.
# Switch to "redis://..." for multi-worker production deployments.
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://", default_limits=[])
