#!/usr/bin/env python2.7
# -*- coding: utf8 -*-
from __future__ import absolute_import, print_function, unicode_literals
"""Script for generating MRCs from stack distances"""
import matplotlib.pyplot as plt
import numpy as np
import pprint, csv
import sys
from datetime import datetime

from cs import CounterStack

# In bytes
_BLOCK_SIZE = 4096
trace = sys.argv[1] #'traces/wdev/wdev_clean.csv' # also available: 'traces/web/web_clean.csv', 'traces/normal_137979.txt'
trace_name = sys.argv[2]
starttime = datetime.now()
def generate_mrc(trace_filename):
	# Set the downsample rate
	downsample_rate = int(sys.argv[3])
	# Create the counterstack and read in the file, feeding it the symbols
	counterstack = CounterStack(downsample_rate)
	steps = 1
	with open(trace_filename, 'r') as f:
		for line in f:
			symbol = line.rstrip()
			counterstack.process_sequence_symbol(symbol)

			if steps % downsample_rate == 0:
				print(steps)
			steps+=1

	print("total time taken to generate curve")
	totaltime = datetime.now() - starttime
	print (totaltime)
	totalsize = counterstack.total_size()
	print("total size in bytes")
	print(totalsize)

	# Get the histogram of stack distances
	bins, values = counterstack.get_stack_distance_counts()

	# Print all the counts
	#pp = pprint.PrettyPrinter(indent=4)
	#pp.pprint(zip(bins, values))
	# Print the total cumulative sum of all counts
	#print(np.sum(values))

	# Make bins in terms of GB
	bins = [bin*_BLOCK_SIZE/float(1000000000) for bin in bins]
	# Carry any fully negative buckets over to the next non-negative bucket (to make the resulting graph monotonically increasing)
	neg = 0
	total = 0
	cum_vals = []
	for i in xrange(len(bins)):
		val = values[i]
		if neg < 0:
			val += neg

		if val < 0:
			neg = val
		else:
			neg = 0
			total += val

		cum_vals.append(1-total/float(steps))

	# vals = np.cumsum(stack_dist_counts.values())/float(steps)
	# vals = np.cumsum(values)

	plt.plot(bins, cum_vals)
	# plt.hist(vals, bins=bins, histtype='step', cumulative=True)# , bins=stack_dist_counts.keys()) # plt.hist#, histtype='step')#, weights=np.zeros_like(stack_dist_counts.values()) + 1./(np.sum(np.array(stack_dist_counts.values()))))
	plt.title(trace_name+"_MRC_sample_" +str(downsample_rate))
	plt.xlabel("Cache Size (GB)")
	plt.ylabel("Miss Ratio")
	plt.ylim(0,1)
	plt.yticks([0.00, 0.25, 0.50, 0.75, 1.00])
	plt.savefig(trace_name+'_MRC_sample_'+str(downsample_rate))


	csv_title = trace_name + '_sample_' + str(downsample_rate)

	# Write results to a csv file
	with open(trace_name+'_mrc_result_sample_' + str(downsample_rate)+'.csv', 'wb') as csvfile:
		# fieldnames = ['bucket', 'cumulative_cache_size']
		writer = csv.writer(csvfile)
		# writer.writeheader()
		for key, value in dict(zip(bins, cum_vals)).items():
			writer.writerow([key, value])

	with open('performance.csv', 'a') as csvfile:
		# fieldnames = ['bucket', 'cumulative_cache_size']
		writer = csv.writer(csvfile)
		# writer.writeheader()
		writer.writerow([csv_title, totaltime, totalsize])

if __name__ == '__main__':
	generate_mrc(trace)
