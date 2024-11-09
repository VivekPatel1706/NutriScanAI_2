import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from Database import retrieve_data
from streamlit_app import url, db, user_collection

def pie_graph(variable=None, top=None, color=None, count_types=False, days=7):
    try:
        documents = retrieve_data(url, db, user_collection)
        data = pd.DataFrame(list(documents))
    except Exception as e:
        print(f"Problem with Retrieving Data: {e}")
        return None  # Exit if there is an issue with data retrieval

    data['date'] = pd.to_datetime(data['date'])

    # Filter data based on the number of past days specified
    start_date = datetime.now() - timedelta(days=days)
    filtered_data = data[data['date'] >= start_date]

    if count_types:
        type_columns = ['type3', 'type2', 'type1', 'type0']
        type_counts = {col: filtered_data[col].notna().sum() for col in type_columns}

        labels = list(type_counts.keys())
        sizes = list(type_counts.values())
    else:
        if variable not in filtered_data.columns:
            raise ValueError(f"Column {variable} not found in the data")

        variables = filtered_data[variable].dropna()
        variable_count = Counter(variables)

        df = pd.DataFrame(variable_count.items(), columns=[variable, 'Count'])
        df['Count'] = pd.to_numeric(df['Count'], errors='coerce')
        df = df.dropna(subset=['Count'])

        if top is not None and top > len(df):
            top = len(df)

        top_variables = df.nlargest(top, 'Count')
        other_variables = df.loc[~df[variable].isin(top_variables[variable]), 'Count'].sum()

        other_df = pd.DataFrame({variable: ['Other'], 'Count': [other_variables]})
        top_variables = pd.concat([top_variables, other_df], ignore_index=True)
        top_variables = top_variables.query('Count != 0')

        labels = top_variables[variable].tolist()
        sizes = top_variables['Count'].tolist()

    # Check for empty sizes
    if len(sizes) == 0 or all(size == 0 for size in sizes):
        print("No valid sizes to plot.")
        return None

    if len(labels) != len(sizes):
        raise ValueError("Length of labels must match length of sizes")

    if color is not None:
        if len(color) == len(sizes) - 1:
            color.append('white')
        elif len(color) + 1 == len(sizes):
            pass
        else:
            raise ValueError("Length of color must match length of sizes")
    else:
        color = plt.get_cmap('tab10').colors
        color = color[:len(sizes)]

    if len(color) < len(sizes):
        raise ValueError("Insufficient number of colors provided")

    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Plot pie chart
    wedges, texts, autotexts = ax.pie(
        sizes, 
        labels=labels, 
        colors=color, 
        startangle=140, 
        autopct='%1.1f%%',
        wedgeprops=dict(edgecolor='black', linewidth=0.5)
    )

    # Customize text appearance
    for autotext in autotexts:
        autotext.set_fontweight('normal')  # Ensure percentage text is not bold

    for text in texts:
        text.set_fontweight('bold')  # Set the label text to bold
        text.set_color('white')  # Adjust label color if needed
        text.set_fontsize(10)  # Adjust label size

    ax.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.

    # Calculate the total for percentage calculation
    total = sum(sizes)
    
    # Add percentages to the radius lines
    for i, p in enumerate(wedges):
        # Calculate the percentage for the current slice
        percentage = sizes[i] / total * 100
        # Get the angle of the slice's midpoint
        ang = (p.theta2 - p.theta1) / 2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))

        # Adjust rotation for better readability
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        rotation_angle = ang if x > 0 else ang + 180  # Adjust rotation for readability
        ax.annotate(f'{percentage:.1f}%', xy=(x, y), xytext=(x * 0.7, y * 0.7),
                    horizontalalignment=horizontalalignment, verticalalignment='center',
                    rotation=rotation_angle, color='black', fontsize=10)

    # Remove the default annotations
    for autotext in autotexts:
        autotext.set_visible(False)

    fig.patch.set_alpha(0)  # Makes the figure background transparent
    ax.set_facecolor('none')
    plt.tight_layout()
    return fig

def line_graph(x_axis=None, y_axis=None, days=7, total_users=False):
    # Retrieve data from the database
    try:
        documents = retrieve_data(url, db, user_collection)
        data = pd.DataFrame(list(documents))
    except Exception as e:
        print(f"Problem with Retrieving Data: {e}")
        return
    
    # Convert the date column to datetime
    data['date'] = pd.to_datetime(data['date'])
    
    # Filter data for the specified number of days
    start_date = datetime.now() - timedelta(days=days)
    filtered_data = data[data['date'] >= start_date]
    
    # If both total_users and x_axis/y_axis are provided, raise an error
    if total_users and (x_axis or y_axis):
        raise ValueError("Cannot plot both total users and specific x and y axes at the same time. Please choose one.")
    
    # Case 1: If `total_users` is True, plot total user count day by day
    if total_users:
        daily_user_count = filtered_data.groupby(filtered_data['date'].dt.date).size()

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(daily_user_count.index, daily_user_count.values, marker='o', label='Total Users', alpha=0.75)

        ax.set_title(f'Total Users Over the Last {days} Days', color='white', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', color='white', fontsize=12)
        ax.set_ylabel('Total Users', color='white', fontsize=12)

        ax.tick_params(axis='x', colors='white', rotation=45)
        ax.tick_params(axis='y', colors='white')

    # Case 2: If `x_axis` and `y_axis` are provided, plot based on the grouping of these axes
    elif x_axis and y_axis:
        if x_axis not in filtered_data.columns or y_axis not in filtered_data.columns:
            raise ValueError(f"Columns {x_axis} or {y_axis} not found in the data")
        
        aggregated_data = filtered_data.groupby([x_axis, y_axis]).size().unstack(fill_value=0)

        fig, ax = plt.subplots(figsize=(12, 6))
        for category in aggregated_data.columns:
            ax.plot(aggregated_data.index, aggregated_data[category], marker='o', label=category, alpha=0.75)

        ax.set_title(f'{y_axis} by {x_axis} Over the Last {days} Days', color='white', fontsize=14, fontweight='bold')
        ax.set_xlabel(x_axis, color='white', fontsize=12)
        ax.set_ylabel('Count', color='white', fontsize=12)

        ax.tick_params(axis='x', colors='white', rotation=45)
        ax.tick_params(axis='y', colors='white')

    # Common plot settings
    legend = ax.legend()
    legend.get_frame().set_edgecolor('none')
    legend.get_frame().set_facecolor('none')
    for text in legend.get_texts():
        text.set_color('white')
    for spine in ax.spines.values():
        spine.set_edgecolor('white')
        spine.set_linewidth(1)

    ax.grid(False)

    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    
    plt.tight_layout()
    return fig

def stacked_bar_graph(x_axis=None, y_axis=None, days=7, top=None):
    """
    Generate a stacked bar graph for the specified x and y axes.

    :param x_axis: Column for the x-axis (e.g., state).
    :param y_axis: Column for stacking on the y-axis (e.g., gender).
    :param days: Number of days to filter data.
    :param top: Number of top x-axis categories to display.
    """
    # Retrieve data from the database
    try:
        documents = retrieve_data(url, db, user_collection)
        data = pd.DataFrame(list(documents))
    except Exception as e:
        print(f"Problem with Retrieving Data: {e}")
        return None
    
    # Convert the date column to datetime
    data['date'] = pd.to_datetime(data['date'])
    
    # Filter data for the specified number of days
    start_date = datetime.now() - timedelta(days=days)
    filtered_data = data[data['date'] >= start_date]

    # Check if the x_axis and y_axis columns exist
    if x_axis not in filtered_data.columns or y_axis not in filtered_data.columns:
        raise ValueError(f"Columns {x_axis} or {y_axis} not found in the data")
    
    # Group and aggregate data
    aggregated_data = filtered_data.groupby([x_axis, y_axis]).size().unstack(fill_value=0)

    # Handle the 'top' parameter
    if top is not None:
        top_x_values = aggregated_data.sum(axis=1).nlargest(top).index
        aggregated_data = aggregated_data.loc[top_x_values]

    # Create the stacked bar plot
    fig, ax = plt.subplots(figsize=(12, 6))
    aggregated_data.plot(kind='bar', stacked=True, ax=ax, colormap='tab20')

    ax.set_title(f'Stacked Bar Graph of {y_axis} by {x_axis} Over the Last {days} Days', 
                 color='white', fontsize=14, fontweight='bold')
    ax.set_xlabel(x_axis.capitalize(), color='white', fontsize=12)
    ax.set_ylabel('Count', color='white', fontsize=12)

    ax.tick_params(axis='x', colors='white', rotation=45)
    ax.tick_params(axis='y', colors='white')

    # Customize legend
    legend = ax.legend(title=y_axis.capitalize())
    legend.get_frame().set_edgecolor('none')
    legend.get_frame().set_facecolor('none')
    for text in legend.get_texts():
        text.set_color('white')

    # Customize axis appearance
    for spine in ax.spines.values():
        spine.set_edgecolor('white')

    ax.grid(False)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    
    plt.tight_layout()
    return fig