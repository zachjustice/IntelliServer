from db import connect, format_data_for_jatin

conn, _ = connect()
ingredient_counts, recipes = format_data_for_jatin(conn)
print ingredient_counts
print recipes
