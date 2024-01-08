file_url='https://ifood-data-architect-test-source.s3-sa-east-1.amazonaws.com/consumer.csv.gz'
curl -sSL "$file_url" | gzip -d > /tmp/customers.csv