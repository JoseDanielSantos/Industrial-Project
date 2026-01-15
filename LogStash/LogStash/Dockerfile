FROM docker.elastic.co/logstash/logstash:9.1.4

# Remove potentially problematic plugins
RUN bin/logstash-plugin remove logstash-input-heartbeat
RUN bin/logstash-plugin remove logstash-filter-sleep

# Reinstall only necessary plugins
RUN bin/logstash-plugin install logstash-input-stdin
RUN bin/logstash-plugin install logstash-output-elasticsearch
RUN bin/logstash-plugin install logstash-output-stdout
