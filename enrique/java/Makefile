JAVAC=javac
JAVA=java
NAME_BINARY=CRFTest
NAME_CONTINUOUS=CRFContinuousTest
SOURCES=$(NAME_BINARY).java $(NAME_CONTINUOUS).java
CFLAGS=-g
CLASSPATH=-cp .:mallet.jar:mallet-deps.jar
FILES_BINARY=../processed_data/train.txt ../processed_data/test.txt
FILES_CONTINUOUS=../processed_data/train_con.txt ../processed_data/test_con.txt

build: $(SOURCES)
	$(JAVAC) $(CFLAGS) $(CLASSPATH) $(SOURCES)

run_binary: $(CLASS)
	$(JAVA) $(CLASSPATH) $(NAME_BINARY) $(FILES_BINARY)

run_continuous: $(CLASS)
	$(JAVA) $(CLASSPATH) $(NAME_CONTINUOUS) $(FILES_CONTINUOUS)
clean:
	rm *.class
