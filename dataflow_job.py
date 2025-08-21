import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.transforms.window import FixedWindows
from apache_beam.io.gcp.pubsub import ReadFromPubSub
from apache_beam.io.gcp.bigquery import WriteToBigQuery
import argparse

class ParseStockRecord(beam.DoFn):
    def process(self, element):
        record = json.loads(element.decode('utf-8'))
        yield record

class FormatForBQ(beam.DoFn):
    def process(self, element, window=beam.DoFn.WindowParam):
        symbol, prices = element
        avg_price = sum(prices) / len(prices)
        yield {
            'symbol': symbol,
            'window_start': window.start.to_utc_datetime(),
            'window_end': window.end.to_utc_datetime(),
            'avg_price': avg_price
        }

def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True)
    parser.add_argument('--region', required=True)
    parser.add_argument('--temp_location', required=True)
    parser.add_argument('--staging_location', required=True)
    parser.add_argument('--input_topic', required=True)
    parser.add_argument('--output_table', required=True)
    known_args, _ = parser.parse_known_args(argv)

    pipeline_options = PipelineOptions(argv)
    pipeline_options.view_as(StandardOptions).streaming = True

    with beam.Pipeline(options=pipeline_options) as p:
        (p
         | 'ReadFromPubSub' >> ReadFromPubSub(topic=known_args.input_topic)
         | 'ParseJson' >> beam.ParDo(ParseStockRecord())
         | 'Window' >> beam.WindowInto(FixedWindows(60))
         | 'KeyBySymbol' >> beam.Map(lambda r: (r['symbol'], r['price']))
         | 'GroupPrices' >> beam.GroupByKey()
         | 'FormatForBigQuery' >> beam.ParDo(FormatForBQ())
         | 'WriteToBigQuery' >> WriteToBigQuery(
                known_args.output_table,
                schema='symbol:STRING,window_start:TIMESTAMP,window_end:TIMESTAMP,avg_price:FLOAT',
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER
         )
        )

if __name__ == '__main__':
    run()
