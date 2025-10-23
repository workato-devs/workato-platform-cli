# flake8: noqa

if __import__("typing").TYPE_CHECKING:
    # import apis into api package
    from workato_platform.client.workato_api.api.api_platform_api import APIPlatformApi
    from workato_platform.client.workato_api.api.connections_api import ConnectionsApi
    from workato_platform.client.workato_api.api.connectors_api import ConnectorsApi
    from workato_platform.client.workato_api.api.data_tables_api import DataTablesApi
    from workato_platform.client.workato_api.api.export_api import ExportApi
    from workato_platform.client.workato_api.api.folders_api import FoldersApi
    from workato_platform.client.workato_api.api.packages_api import PackagesApi
    from workato_platform.client.workato_api.api.projects_api import ProjectsApi
    from workato_platform.client.workato_api.api.properties_api import PropertiesApi
    from workato_platform.client.workato_api.api.recipes_api import RecipesApi
    from workato_platform.client.workato_api.api.users_api import UsersApi
    
else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import apis into api package
from workato_platform.client.workato_api.api.api_platform_api import APIPlatformApi
from workato_platform.client.workato_api.api.connections_api import ConnectionsApi
from workato_platform.client.workato_api.api.connectors_api import ConnectorsApi
from workato_platform.client.workato_api.api.data_tables_api import DataTablesApi
from workato_platform.client.workato_api.api.export_api import ExportApi
from workato_platform.client.workato_api.api.folders_api import FoldersApi
from workato_platform.client.workato_api.api.packages_api import PackagesApi
from workato_platform.client.workato_api.api.projects_api import ProjectsApi
from workato_platform.client.workato_api.api.properties_api import PropertiesApi
from workato_platform.client.workato_api.api.recipes_api import RecipesApi
from workato_platform.client.workato_api.api.users_api import UsersApi

""",
            name=__name__,
            doc=__doc__,
        )
    )
