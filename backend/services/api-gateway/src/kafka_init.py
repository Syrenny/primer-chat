from kafka.admin import KafkaAdminClient, NewTopic
from shared_config import config


def init_kafka() -> None:
    admin = KafkaAdminClient(bootstrap_servers=config.kafka.bootstrap_servers)

    topics = [
        NewTopic(
            name=config.kafka.indexation.request.topic,
            num_partitions=config.kafka.defaults.partitions,
            replication_factor=config.kafka.defaults.replication_factor,
        ),
        NewTopic(
            name=config.kafka.indexation.response.topic,
            num_partitions=config.kafka.defaults.partitions,
            replication_factor=config.kafka.defaults.replication_factor,
        ),
        NewTopic(
            name=config.kafka.generation.request.topic,
            num_partitions=config.kafka.defaults.partitions,
            replication_factor=config.kafka.defaults.replication_factor,
        ),
    ]

    existing = admin.list_topics()
    to_create = [t for t in topics if t.name not in existing]

    if to_create:
        admin.create_topics(to_create)
        print("✅ Topics created")
    else:
        print("ℹ️ All topics already exist")
