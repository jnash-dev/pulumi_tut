"""A Python Pulumi program"""

import pulumi
import pulumi_docker as docker # type: ignore

# Get configuration values
config = pulumi.Config()
frontend_port = config.require_int("frontendPort")
backend_port = config.require_int("backendPort")
mongo_port = config.require_int("mongoPort")
mongo_host = config.require("mongoHost") # Note that strings are the default, so it's not `config.require_str`, just `config.require`.
database = config.require("database")
node_environment = config.require("nodeEnvironment")
protocol = config.require("protocol")
mongo_username = config.require("mongoUsername")
mongo_password = config.require_secret("mongoPassword")

stack = pulumi.get_stack()

# Pull the backend image
backend_image_name = "backend"
backend = docker.RemoteImage(
    f"{backend_image_name}_image",
    name="pulumi/tutorial-pulumi-fundamentals-backend:latest",
)

# Pull the frontend image
frontend_image_name = "frontend"
frontend = docker.RemoteImage(
    f"{frontend_image_name}_image",
    name="pulumi/tutorial-pulumi-fundamentals-frontend:latest",
)

# Pull the MongoDB image
mongo_image = docker.RemoteImage(
    "mongo_image", name="pulumi/tutorial-pulumi-fundamentals-database:latest"
)

# Create a Docker network
network = docker.Network("network", name=f"services_{stack}")

# Create the MongoDB container
mongo_container = docker.Container(
    "mongo_container",
    image=mongo_image.repo_digest,
    name=f"mongo-{stack}",
    ports=[docker.ContainerPortArgs(internal=mongo_port, external=mongo_port)],
    networks_advanced=[docker.ContainerNetworksAdvancedArgs(name=network.name, aliases=["mongo"])],
    envs=[
        f"MONGO_INITDB_ROOT_USERNAME={mongo_username}",
        mongo_password.apply(lambda password: f"MONGO_INITDB_ROOT_PASSWORD={password}"),
    ],
)

# Create the backend container
backend_container = docker.Container(
    "backend_container",
    image=backend.repo_digest,
    name=f"backend-{stack}",
    ports=[docker.ContainerPortArgs(internal=backend_port, external=backend_port)],
    envs=[
        pulumi.Output.concat(
            "DATABASE_HOST=mongodb://",
            mongo_username,
            ":",
            mongo_password,
            "@",
            mongo_host,
            ":",
            f"{mongo_port}",
        ),  # Changed!
        f"DATABASE_NAME={database}?authSource=admin",  # Also changed!
        f"NODE_ENV={node_environment}",
    ],
    networks_advanced=[docker.ContainerNetworksAdvancedArgs(name=network.name)],
    opts=pulumi.ResourceOptions(depends_on=[mongo_container]),
)

# Create the frontend container
frontend_container = docker.Container(
    "frontend_container",
    image=frontend.repo_digest,
    name=f"frontend-{stack}",
    ports=[docker.ContainerPortArgs(internal=frontend_port, external=frontend_port)],
    envs=[
        f"PORT={frontend_port}",
        f"HTTP_PROXY=backend-{stack}:{backend_port}",
        f"PROXY_PROTOCOL={protocol}",
    ],
    networks_advanced=[docker.ContainerNetworksAdvancedArgs(name=network.name)],
)

pulumi.export("url", pulumi.Output.format("http://localhost:{0}", frontend_port))
pulumi.export("mongoPassword", mongo_password)