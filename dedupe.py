class CsvDeDuper():
	def __init__(self, filename):
		self.filename = filename
		self.output_filename = filename.replace(".csv", "_deduped.csv")
		self.csv_content = ""

		with open(self.filename, "r") as csv_reader:
			self.csv_content = csv_reader.read()

		self.dedupe()
		self.write_output()

	def dedupe(self):
		tweet_cache = []

		csv_lines = self.csv_content.split("\n")

		self.csv_output = ""

		# Debugging purposes
		line_no = 0
		rejected_count = 0
		for csv_line in csv_lines:
			columns = csv_line.split(";")

			# If tweet in cache, reject
			if columns[0] in tweet_cache:
				line_no += 1
				rejected_count += 1
				continue

			self.csv_output += csv_line + "\n"
			tweet_cache.append(columns[0])

			line_no =+ 1

		print("Removed", rejected_count, "items.")

	def write_output(self):
		with open(self.output_filename, "w") as csv_writer:
			csv_writer.write(self.csv_output)

		print("Wrote deduped output to file")

CsvDeDuper("corpus/corpus_zijt.csv")
CsvDeDuper("corpus/corpus_bent.csv")