import matplotlib.pyplot as plt
import numpy as np

def plot_partograph():
    # Time in hours from 4 cm cervical dilation (start of active labor)
    hours = np.arange(0, 12, 0.5)

    # Alert line: 1 cm/hour dilation from 4 cm to 10 cm (normal progress)
    alert_line = 4 + hours

    # Action line: 4 hours delayed from alert line
    action_line = 4 + np.maximum(hours - 4, 0)

    # Example cervical dilation curves:
    # Normal progress: steady 1 cm/hr dilation
    normal_dilation = np.minimum(4 + hours, 10)

    # Slow progress (dystocia): nearly flat from 4-7 cm, then slow dilation
    slow_dilation = np.piecewise(hours, [hours < 3, hours >= 3], [4, lambda x: 4 + 0.5*(x-3)])
    slow_dilation = np.minimum(slow_dilation, 10)

    # Fetal head descent stations (from -3 to +3)
    # Normal descent: gradual from -3 to +3 over 8 hours
    descent_time = np.arange(0, 9, 1)
    normal_descent = -3 + (6/8) * descent_time  # linear from -3 to +3
    slow_descent = np.full_like(descent_time, -1)  # no descent in slow labor

    # Plotting the partograph
    plt.figure(figsize=(12, 8))

    # Subplot 1 - Cervical dilation with alert and action lines
    plt.plot(hours, alert_line, 'g--', label='Alert Line (1 cm/hr)')
    plt.plot(hours, action_line, 'r--', label='Action Line (+4 hrs)')
    plt.plot(hours, normal_dilation, 'b-', lw=2, label='Normal Lab. Progress')
    plt.plot(hours, slow_dilation, 'm-', lw=2, label='Slow Progress (Dystocia)')

    plt.xlabel('Time since 4 cm dilation (hours)')
    plt.ylabel('Cervical Dilation (cm)')
    plt.title('Partograph - Cervical Dilation Progress')
    plt.xlim(0, 12)
    plt.ylim(0, 11)
    plt.legend()
    plt.grid(True)

    # Subplot 2 - Fetal head descent over time
    plt.figure(figsize=(12, 4))
    plt.plot(descent_time, normal_descent, 'b-o', label='Normal Fetal Descent')
    plt.plot(descent_time, slow_descent, 'r-o', label='No Descent (Dystocia)')
    plt.xlabel('Time (hours)')
    plt.ylabel('Fetal Head Station')
    plt.title('Fetal Head Descent Over Time')
    plt.yticks(np.arange(-3, 4, 1))
    plt.legend()
    plt.grid(True)

    # Subplot 3 - Sample uterine contractions pattern
    plt.figure(figsize=(12, 4))
    time_contractions = np.arange(0, 60, 5)  # minutes
    strength_normal = 3 + 2 * np.sin(np.linspace(0, 6*np.pi, len(time_contractions)))  # contractions strength
    strength_weak = 1 + np.sin(np.linspace(0, 6*np.pi, len(time_contractions)))       # weak contractions

    plt.plot(time_contractions, strength_normal, 'g-', label='Normal Contractions')
    plt.plot(time_contractions, strength_weak, 'r-', label='Weak Contractions (Power Deficiency)')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Contraction Strength (arbitrary units)')
    plt.title('Sample Uterine Contraction Patterns')
    plt.legend()
    plt.grid(True)

    # Subplot 4 - Example fetal heart rate trend during labor
    plt.figure(figsize=(12, 4))
    time_fhr = np.arange(0, 60, 1)
    # Normal baseline with accelerations
    fhr_normal = 140 + 10*np.sin(0.2*time_fhr) + 5*np.random.normal(size=len(time_fhr))
    # Fetal distress pattern: decelerations and reduced variability
    fhr_distress = 130 + 5*np.sin(0.05*time_fhr) + 2*np.random.normal(size=len(time_fhr))

    plt.plot(time_fhr, fhr_normal, 'b-', label='Normal Fetal Heart Rate')
    plt.plot(time_fhr, fhr_distress, 'r-', label='Distress Pattern')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Fetal Heart Rate (bpm)')
    plt.title('Fetal Heart Rate Patterns during Labor')
    plt.legend()
    plt.grid(True)

    plt.show()

if __name__ == "__main__":
    plot_partograph()
