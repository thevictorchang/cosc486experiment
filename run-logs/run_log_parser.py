# import file
import os

"""
Example lines...

['1484789602.955921', 'TASKCONFIG', 'NEGATIVE', 'NEGATIVE_EXPERIENCE', '6', '-1', '4', '6.005668924097853', '7.008428622070581']
['1484789603.779311', 'MOUSEDOWN', '1042', '275']
['1484789603.779311', 'SNAPPING', 'True']
['1484789603.779311', 'STARTDRAG']
['1484789604.411338', 'MOUSEUP', '1389', '782']
['1484789605.107999', 'MOUSEDOWN', '1048', '848']
['1484789605.107999', 'SNAPPING', 'False']
['1484789605.107999', 'STARTDRAG']
['1484789607.619967', 'MOUSEUP', '1049', '532']
['1484789607.620478', 'COMPLETE']
['1484789615.387655', 'PREFERENCE', 'ON']
"""

file_name = 'subject-2.txt'
participant_id = int(file_name.split('.')[0].split('-')[1])
run_log_file_lines = open(file_name, 'r').readlines()

'''setup everything after practice in runlog file as a list '''


def disregard_practice(run_log_file_lines):
    run_log_file_lines_list = []
    endpractise_index = 0
    i = 0
    for line in run_log_file_lines:
        log_file_line = line.strip().split('\t')
        run_log_file_lines_list.append(log_file_line)
        if (log_file_line[1] == 'ENDPRACTISE'):
            endpractise_index = i
        i += 1

    return run_log_file_lines_list[(endpractise_index + 1):]


all_preferences = []  # list of dictionaries of format {framing:, positive:, negative:, neutral:}
positive_framing_positive_task_times = []
positive_framing_negative_task_times = []
positive_framing_neutral_task_times = []  # control tasks
negative_framing_positive_task_times = []
negative_framing_negative_task_times = []
negative_framing_neutral_task_times = []  # control tasks

for file in os.listdir("."):

    if file.endswith(".txt"):

        participant_preferences_dictionary = {}

        participant_id = int(file.split('.')[0].split('-')[1])
        positive_framing = None

        #print(participant_id)
        if (participant_id % 2 == 0):
            participant_preferences_dictionary["framing"] = "positive"
            positive_framing = True
        else:
            participant_preferences_dictionary["framing"] = "negative"
            positive_framing = False

        run_log_file_lines_list = disregard_practice(open(file, 'r').readlines())

        current_experience = ""  # 'experience' being a sequence of tasks. for preference logging purposes.
        first_mousedown = False  # Made a mousedown in the trial yet?
        start_time = 0  # Trial start time
        current_task = ""  # 'task' being one "drag black box to white box" task. For task time logging purposes.

        for line in run_log_file_lines_list:
            timestamp = float(line[0])

            if line[1] == 'TASKCONFIG':
                current_task = line[2].lower()
                if (line[3] != current_experience):  # if we are now in a new experience
                    current_experience = line[3]
                    first_mousedown = False


            elif line[1] == 'PREFERENCE':
                participant_preferences_dictionary[current_experience.lower()] = line[2].lower()

            elif line[1] == 'MOUSEDOWN' and not first_mousedown:
                first_mousedown = True
                start_time = timestamp

            elif line[1] == 'COMPLETE':
                duration = timestamp - start_time
                if (current_task == 'positive'):
                    if positive_framing:
                        positive_framing_positive_task_times.append(duration)
                    else:
                        negative_framing_positive_task_times.append(duration)
                elif (current_task == 'negative'):
                    if positive_framing:
                        positive_framing_negative_task_times.append(duration)
                    else:
                        negative_framing_negative_task_times.append(duration)
                elif (current_task == 'neutral'):
                    if positive_framing:
                        positive_framing_neutral_task_times.append(duration)
                    else:
                        negative_framing_neutral_task_times.append(duration)
        #print(participant_preferences_dictionary)
        all_preferences.append(participant_preferences_dictionary)

#print(all_preferences)
# each tuple will have two elements, (no_grid_snap_on, no_grid_snap_off)
positive_framing_positive_experience = {'on': 0, 'off': 0}
positive_framing_negative_experience = {'on': 0, 'off': 0}
positive_framing_neutral_experience = {'on': 0, 'off': 0}
negative_framing_positive_experience = {'on': 0, 'off': 0}
negative_framing_negative_experience = {'on': 0, 'off': 0}
negative_framing_neutral_experience = {'on': 0, 'off': 0}

for participant_preferences in all_preferences:
    #print(participant_preferences)
    if (participant_preferences["framing"] == "positive"):

        if (participant_preferences["negative_experience"] == "on"):
            positive_framing_negative_experience['on'] += 1
        else:
            positive_framing_negative_experience['off'] += 1

        if participant_preferences['positive_experience'] == 'on':
            positive_framing_positive_experience['on'] += 1
        else:
            positive_framing_positive_experience['off'] += 1



        if (participant_preferences["neutral_experience"] == "on"):
            positive_framing_neutral_experience['on'] += 1
        else:
            positive_framing_neutral_experience['off'] += 1

    if (participant_preferences["framing"] == "negative"):
        if (participant_preferences["positive_experience"] == "on"):
            negative_framing_positive_experience['on'] += 1
        else:
            negative_framing_positive_experience['off'] += 1

        if (participant_preferences["negative_experience"] == "on"):
            negative_framing_negative_experience['on'] += 1
        else:
            negative_framing_negative_experience['off'] += 1

        if (participant_preferences["neutral_experience"] == "on"):
            negative_framing_neutral_experience['on'] += 1
        else:
            negative_framing_neutral_experience['off'] += 1

results_file = open('results', 'w')

print("positive_framing_positive_experience: " + str(positive_framing_positive_experience))
results_file.write("positive_framing_positive_experience: " + str(positive_framing_positive_experience) + "\n")
print("positive_framing_negative_experience: " + str(positive_framing_negative_experience))
results_file.write(("positive_framing_negative_experience: " + str(positive_framing_negative_experience)) + "\n")
print("positive_framing_neutral_experience: " + str(positive_framing_neutral_experience))
results_file.write(("positive_framing_neutral_experience: " + str(positive_framing_neutral_experience)) + "\n")
print("negative_framing_positive_experience: " + str(negative_framing_positive_experience))
results_file.write(("negative_framing_positive_experience: " + str(negative_framing_positive_experience)) + "\n")
print("negative_framing_negative_experience: " + str(negative_framing_negative_experience))
results_file.write(("negative_framing_negative_experience: " + str(negative_framing_negative_experience)) + "\n")
print("negative_framing_neutral_experience: " + str(negative_framing_neutral_experience))
results_file.write("negative_framing_neutral_experience: " + str(negative_framing_neutral_experience) + "\n")

print("")
results_file.write("" + "\n")

print("positive_framing_positive_task_times: " + str(positive_framing_positive_task_times))
results_file.write("positive_framing_positive_task_times: " + str(positive_framing_positive_task_times) + "\n")
print("positive_framing_negative_task_times: " + str(positive_framing_negative_task_times))
results_file.write("positive_framing_negative_task_times: " + str(positive_framing_negative_task_times) + "\n")
print("positive_framing_neutral_task_times: " + str(positive_framing_neutral_task_times))
results_file.write("positive_framing_neutral_task_times: " + str(positive_framing_neutral_task_times) + "\n")

print("")
results_file.write("" + "\n")

print("negative_framing_positive_task_times: " + str(negative_framing_positive_task_times))
results_file.write("negative_framing_positive_task_times: " + str(negative_framing_positive_task_times) + "\n")
print("negative_framing_negative_task_times: " + str(negative_framing_negative_task_times))
results_file.write("negative_framing_negative_task_times: " + str(negative_framing_negative_task_times) + "\n")
print("negative_framing_neutral_task_times: " + str(negative_framing_neutral_task_times))
results_file.write("negative_framing_neutral_task_times: " + str(negative_framing_neutral_task_times) + "\n")



