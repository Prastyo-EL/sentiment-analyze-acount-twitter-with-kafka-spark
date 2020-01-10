# sentiment-analyze-acount-twitter-with-kafka-spark
langkah-langkah untuk menjalankan sentiment-analyze-acount-twitter-with-kafka-spark
1.  masuk ke directory kafka misal /opt/kafka jika di linux
2.  setelah masuk ke directory kafka jalankan zookeeper dengan perintah "zookeeper-server-start.sh config/zookeeper.properties"
3.  kemudian setelah zookeeper aktif buka tab baru dan masuk kembali ke directory kafka
4.  jalankan kafka server dengan perintah "kafka-server-start.sh config/server.properties"
5.  kafka_2.11-1.1.0 bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic tweet
    Created topic "tweet".
6.  setelah topic created dan setelah semua berjalan masuk ke directory penyimpanan sentiment-analyze-acount-twitter-with-kafka-spark
8.  langsung jalankan "main.py" dengan perintah "python main.py tweet
9.  buka tab baru ketikan perintah "spark-submit --master local[1] --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.1.0 oretan_spark_eko.py localhost:9092 tweet 10" untuk menjalankan spark
10. local[1] menunjukan hanya menjalankan 1 core
11. kemudian kembali ke tab "main.py" click "http://localhost:5002/" langsung akan ke webserver
