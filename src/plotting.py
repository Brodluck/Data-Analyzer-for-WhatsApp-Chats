import matplotlib.pyplot as plt


def plot_time_ranges(time_ranges, filename="time_ranges_plot.png"):
    fig, ax = plt.subplots()
    ax.plot(range(len(time_ranges)), time_ranges)
    ax.set_xlabel('Time Range')
    ax.set_ylabel('Number of Messages')
    ax.set_title('Message Density Over Time')
    fig.savefig(filename)
    plt.close(fig) 

def plot_sender_count(sender_count, filename="sender_count_plot.png"):
    fig, ax = plt.subplots()
    ax.bar(sender_count.keys(), sender_count.values())
    ax.set_xlabel('Sender')
    ax.set_ylabel('Number of Messages')
    ax.locator_params(axis='y', integer=True)
    ax.set_title('Message Count per Sender')
    ax.tick_params(axis='x', rotation=45)
    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)

def plot_sender_percentage(sender_percentage, filename="sender_percentage_plot.png"):
    fig, ax = plt.subplots()
    labels = sender_percentage.keys()
    sizes = sender_percentage.values()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    ax.set_title('Percentage of Messages Sent by Each Sender')
    fig.savefig(filename)
    plt.close(fig)