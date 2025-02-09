import numpy as np
from nicegui import ui
from matplotlib import pyplot as plt
import seaborn as sns

def create_plots(params, fig):
    """Generate all demonstration plots with current parameters"""
    # np.random.seed(42)  # Fixed seed for reproducibility
    
    # Unpack parameters
    pop_mean = params['population_mean']
    pop_sd = params['population_sd']
    meas_error = params['measurement_error']
    n_people = params['n_people']
    count = params['count']

    k=4  # Number of standard deviations to show in plots
    frame_size = k*(15**2+15**2)**.5
    
    # Data generation
    true_heights = np.random.normal(pop_mean, pop_sd, n_people)
    measured_parent = np.random.normal(true_heights, meas_error)
    measured_child = np.random.normal(true_heights, meas_error)
    
    # Identify extremes
    threshold = np.percentile(measured_parent, (1- count/n_people)*100)
    extreme_mask = measured_parent >= threshold
    
    # Create figures
    # fig = plt.figure(figsize=(18, 6))
    ax1, ax2, ax3 = fig.subplots(1, 3)
    
    # Plot 1: Full population comparison
    sns.scatterplot(x=measured_parent, y=measured_child, ax=ax1, alpha=0.7)
    ax1.plot([pop_mean-frame_size, pop_mean+frame_size], [pop_mean-frame_size, pop_mean+frame_size], '--', color='gray')
    ax1.set_title("Full Population")
    ax1.set_xlabel("Parent Height")
    ax1.set_ylabel("Child Height")
    ax1.set_xlim(pop_mean-frame_size, pop_mean+frame_size)
    ax1.set_ylim(pop_mean-frame_size, pop_mean+frame_size)
    
    # Plot 2: Extreme cases analysis
    sns.scatterplot(x=measured_parent[extreme_mask], y=measured_child[extreme_mask], ax=ax2)
    ax2.axhline(pop_mean, color='r', linestyle='--')
    ax2.set_title(f"Top {count} Extremes")
    ax2.set_xlabel("Parent Height")
    ax2.set_xlim(pop_mean-frame_size, pop_mean+frame_size)
    ax2.set_ylim(pop_mean-frame_size, pop_mean+frame_size)
    
    # Plot 3: 1D comparison
    for p, c in zip(measured_parent[extreme_mask], measured_child[extreme_mask]):
        ax3.plot([0, 1], [p, c], 'gray', alpha=0.3)
    sns.stripplot(x=np.zeros(sum(extreme_mask)), y=measured_parent[extreme_mask], 
                  ax=ax3, jitter=0, color='orange', label='Parents')
    sns.stripplot(x=np.ones(sum(extreme_mask)), y=measured_child[extreme_mask], 
                  ax=ax3, jitter=0, color='blue', label='Children')
    ax3.axhline(pop_mean, color='r', linestyle='--')
    ax3.set_xticks([0, 1])
    ax3.set_xticklabels(['Parents', 'Children'])
    ax3.set_title("Height Distributions")
    ax3.set_ylabel("Height")
    ax3.set_ylim(pop_mean-frame_size, pop_mean+frame_size)
    
    parent_mean = measured_parent[extreme_mask].mean()
    child_mean = measured_child[extreme_mask].mean()
    # Add mean lines
    ax3.axhline(parent_mean, color='coral', linestyle='--', alpha=0.7)
    ax3.axhline(child_mean, color='blue', linestyle='--', alpha=0.7)
    ax3.axhline(pop_mean, color='darkred', linestyle='-', alpha=0.7)

    #  Add mean annotations
    ax3.text(0.5, parent_mean+1, f'Parent Mean: {parent_mean:.1f}cm',
            color='coral', ha='center')
    ax3.text(0.5, child_mean-1, f'Child Mean: {child_mean:.1f}cm',
            color='blue', ha='center')
    ax3.text(0.5, pop_mean+1, f'Population Mean: {pop_mean}cm',
            color='darkred', ha='center')
    stats_text = (
        f"Extreme Parents Mean: {parent_mean:.1f} cm\n"
        f"Their Children Mean: {child_mean:.1f} cm\n"
        f"Population Mean: {pop_mean} cm\n"
        f"Regression Effect: {parent_mean - child_mean:.1f} cm"
    )

    
    plt.tight_layout()
    return stats_text

# Create plot containers
plot_row = None

def update_plots():
    """Refresh all plots with current parameters"""
    plot_row.clear()
    params = {
        'population_mean': population_mean.value,
        'population_sd': population_sd.value,
        'measurement_error': measurement_error.value,
        'count': count.value,
        'n_people': n_people.value
    }
    with plot_row:
        with ui.matplotlib(figsize=(18, 6)).figure as fig:
            stats_text = create_plots(params, fig)

        ui.label(stats_text)
        # ui.pyplot(create_plots(None, params)).classes('w-full')

# Create parameter controls
with ui.row().classes('w-full'):
    ui.label('Simulation Parameters')
    with ui.row().classes('w-full'):
        ui.label('Population Mean: ')
        mean_bind = ui.label('170')
    population_mean = ui.slider(min=150, max=190, value=170, step=1).on('change', update_plots)
    mean_bind.bind_text_from(population_mean, 'value')

    with ui.row().classes('w-full'):
        ui.label('Population SD: ')
        sd_bind = ui.label('8')
    population_sd = ui.slider(min=0, max=15, value=8, step=1).on('change', update_plots)
    sd_bind.bind_text_from(population_sd, 'value')

    with ui.row().classes('w-full'):
        ui.label('Measurement Error: ')
        error_bind = ui.label('5')
    measurement_error = ui.slider(min=0, max=15, value=5, step=1).on('change', update_plots)
    error_bind.bind_text_from(measurement_error, 'value')

    with ui.row().classes('w-full'):
        ui.label('Extreme Count: ')
        count_bind = ui.label('90')
    count = ui.slider(min=0, max=100, value=10, step=1).on('change', update_plots)
    count_bind.bind_text_from(count, 'value')

    with ui.row().classes('w-full'):
        ui.label('Number of People: ')
        n_people_bind = ui.label('100')
    n_people = ui.slider(min=500, max=2000, value=1000, step=50).on('change', update_plots)
    n_people_bind.bind_text_from(n_people, 'value')

plot_row = ui.row().classes('w-full')

# Initial plot
update_plots()

# Add refresh button
ui.button('Run Simulation', on_click=update_plots).props('icon=refresh')

# Run the app
ui.run(title="RTM Demo", dark=True)