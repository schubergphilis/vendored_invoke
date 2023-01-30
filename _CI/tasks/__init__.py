from invoke import Collection

import tasks, vendored

namespace = Collection()
namespace.add_collection(vendored)
