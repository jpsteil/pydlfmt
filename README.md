# Python data list Formatter

Take a list of data elements and transform them into a spreadsheet or PDF document.

* Elements can be a dictionary, dataclass or any object
* You specify which columns are to be included in the output
* Columns can have custom formatting

Example - Assuming the `data` variable has been loaded prior to this snippet.
```python
df = DataFormatter(data=data)
df.columns = [
    Column("id"),
    Column("name"),
    Column("sex"),
    Column("age"),
    Column("year"),
    Column("team"),
    Column("sport"),
]
df.to_pdf(filename=os.path.join("../examples", "output", "sample.pdf"))
df.to_excel(
    filename=os.path.join("../examples", "output", "sample.xlsx"),
    format_table=True,
)
```
* Create a DataFormatter instance
* Define the columns that you want included in your output
  * Column `names` are used to match up with the input data column or element names
* Call to_pdf or to_excel to build the output

## Columns
You have a lot of control over how the column is displayed. The `Column` dataclass object has the following attributes.

* name - the name of the column. If your data list is a list of dictionaries, then this should match one of the keys of the dictionary.  It must exist in all rows in the list. If you data list is a list of dataclasses or objects, then this much match one of the attributes of the object that exists in all rows of the list.
* heading - the column heading. Will default to the column name if none provided.
* font_size - default 10 - for PDF, this is override the font size of the cell.
* bold - default False - for PDF only, should this column be bold
* justify - default LEFT - LEFT, CENTER or RIGHT
* scalar - for Excel only - a scalar function that should be run on this column. Valid values are SUM, AVG
* decimal_positions - number of decimal positions to round to
* currency - should we display the $
* excel_formula - an Excel formula that you want run to produce the output for this column
* datatype - defualt str - what is the datatype for this column
* wrap - default False - wrap text to fit in the column
* width - the default width to use for this column
* max_width - the maximum width - use to ensure longer fields get the width they need
* paragraph_style - PDF only - pass in custom reportlab paragraph_style to be applied to all the cells in a column
* include_commas - default False - should we include commas when printing numbers
