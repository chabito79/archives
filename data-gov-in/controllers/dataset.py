import json
import utils, properties
import re
consolelog = []

def get_args(form_dict):
	properties.load_properties()
	file_properties = properties.properties[form_dict["fname"]]
	file_data = utils.get_file_data(form_dict["fname"])
	group = file_properties.get("groups", ["Other"])[0]
	chart_type = file_properties.get("chart_type") or "Line"
	
	args = {
		"file_data": file_data,
		"properties": file_properties,
		"chart_type": chart_type,
		"group": group,
		"group_info": properties.groups[group],
		"consolelog": consolelog,
		"json": json,
		"len": len,
		"title": file_properties.get("title", form_dict["fname"]),
		"description": file_properties.get("description", form_dict["fname"])
	}
	
	if chart_type == "Map":
		args["map_data"] = get_map_data(file_data, file_properties)
		args["legend"] = file_properties.get("legend") or ""
	else:
		args["chart_data"] = get_chart_data(file_data, file_properties, chart_type)
	
	return args
	
def get_chart_data(file_data, file_properties, chart_type):
	global consolelog

	if file_properties.get("transpose"):
		map_dataset = map(list, zip(*file_data))
	else:
		map_dataset = [[val for val in row] for row in file_data]

	map_dataset = exclude_total_type_columns(map_dataset, 1)
	start_row, start_column = get_start_row_and_column(map_dataset)
	value_map_dataset = get_numeric_dataset(map_dataset, start_row, start_column)

	x_labels = file_data[0][1:]
	x_labels = [label[:15] for label in map_dataset[0][start_column:]]
	x_label_color = []
	
	data_sets = []
	color_steps = int(255.0 / (len(value_map_dataset)))
	i = 0
	for row in value_map_dataset:
		i += color_steps
		if chart_type == "Line":
			data_set_row = {
				"fillColor" : "rgba(%i, %i, %i, %s)" % (i, i/1.2, i/4, .3),
				"strokeColor" : "rgba(%i, %i, %i, %s)" % (i, i/1.2, i/4, 1),
				"pointColor" : "rgba(%i, %i, %i, %s)" % (i, i, i/1.2, 1),
				"pointStrokeColor" : "#fff",
				"data": [utils.flt(val) for val in row]
			}
			data_sets.append(data_set_row)
			x_label_color.append(data_set_row["strokeColor"])
		elif chart_type == "Pie":
			data_sets.append({
				"value": utils.flt(row[1]),
				"color": "rgba(%i, %i, %i, %s)" % (i, i/1.2, i/4, .3),
			})
	
	chart_data = {
		"chart_type": chart_type,
		"labels": x_labels,
		"datasets": data_sets
	}
		
	return chart_data
	
def get_map_data(file_data, file_properties):
	global consolelog
	map_dataset = [[val for val in row] for row in file_data]
	start_row, start_column = get_start_row_and_column(map_dataset)
	
	value_function = file_properties.get("value_function")
	if value_function:
		value_function = eval(value_function)
	
	map_labels_column = file_properties.get("map_labels_column") or (start_column - 1)
	
	data_sets = {}
	for i, row in enumerate(map_dataset):
		if i < start_row: continue
		label = row[map_labels_column]
		if value_function:
			data_sets[label] = value_function(row)
		else:
			data_sets[label] = row[start_column]
	
	return data_sets
	
def exclude_total_type_columns(map_dataset, start_row):
	global consolelog
	
	start_row_data = map_dataset[start_row-1]
	original_col_len = len(start_row_data)
	excluded = [cidx for cidx in xrange(original_col_len) \
		if "total" in start_row_data[cidx].lower()]
	new_dataset = []
	for row in map_dataset:
		new_row = []
		new_dataset.append(new_row)
		for cidx in xrange(original_col_len):
			if not cidx in excluded:
				new_row.append(row[cidx])
		# consolelog.append(new_row)
				
	return new_dataset
		

def get_numeric_dataset(map_dataset, start_row, start_column):
	map_dataset = [row[start_column:] for row in map_dataset[start_row:]]
	return map_dataset

def get_start_row_and_column(map_dataset):
	start_column = 1
	start_row = 1
	
	def has_numeric_value(row):
		ret = False
		for value in row:
			if re.search('[0-9.]+', value):
				ret = True
				break
		return ret
		
	while not has_numeric_value(map_dataset[start_row]) and start_row < len(map_dataset):
		start_row += 1
	
	while re.search('[a-zA-Z]+', map_dataset[start_row][start_column]) and start_column < len(map_dataset[start_row]):
		start_column += 1
		if start_column > 20:
			break
			
	return start_row, start_column
	