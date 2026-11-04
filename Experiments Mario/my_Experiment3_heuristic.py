#############################################################################
### Example experiment 3: Scheduling Projects with Resources (Heuristically)
### = Solve the resource-constrained project scheduling problem heuristically with priority rules
###
###   The experiment applies the scheduling techniques of Chapter 8 of Book 1 (reference below)
###
###   The experiment makes use of three projects
###   (Projects 1 and 2 come from the Book 1 and Projet 3 from our huge database (Book 2 and Paper 2)
###      * Project 1 (1 resource). Network of Figure 7.1, resource data from Table 7.1 with schedule of Figure 7.3
###      * Project 2 (4 resources). Network of Figure 7.1, resource data from Table 7.2 with schedule of Figure 7.4
###      * Project 3 (4 resources). File "mv2.rcp" from the DC1 set
###
###    Summary details (from Book 1):
###      - The code contains 13 priority rules
###        * Activity rules
###          ° SPT: Shortest Processing Time
###          ° LPT: Longest Processing Time
###        * Network rules
###          ° MIS: Most Immediate Successors
###          ° MTS: Most Total Successors
###          ° LNRJ: Least Non-Related Jobs
###          ° GRPW: Greatest Rank Positional Weight
###        * Scheduling rules (CPM)
###          ° EST: Earliest Start Time
###          ° EFT: Earliest Finish Time
###          ° LST: Latest Start Time
###          ° LFT: Latest Finish Time
###          ° MSLK: Minimum Slack
###        * Resource rules
###          ° GRWC: Greatest Resource Work Content
###          ° GCRWC: Greatest Cumulative Resource Work Content
###      - The schedules are generated using two schedule generation schemes
###        * Serial schedule generation: Schedule activities one at a time, as soon as possible (activity incrementation)
###        * Parallel schedule generation: Schedule multiple activities at each time period with resource availability (time incrementation)
###
###    References
###     Book 1:
###      - Title: Project Management with Dynamic Scheduling: Baseline Scheduling, Risk Analysis and Project Control
###      - Author: Mario Vanhoucke
###      - Year: 2013
###      - Publisher: Springer
###      - Source: https://doi.org/10.1007/978-3-642-40438-2
###
###     Book 2: 
###      - The search for data to solve the resource-constrained project scheduling problem has been described in the following book:
###        (Note that the DC1 is also described in this book)
###        * Title: A Quest for Projects with Scarce Resources: Seeking Schedule Intelligence Through Project Data Discovery
###        * Author: Mario Vanhoucke
###        * Year: 2025
###        * Publisher: Springer
###        * Source: https://doi.org/10.1007/978-3-031-71507-5
###
###     Paper 1:
###      - The DC1 (project 3) has been generated a long time ago in the following study:
###        * Title: On maximizing the net present value of a project under renewable resource constraints
###        * Author: Mario Vanhoucke, Erik Demeulemeester and Willy Herroelen
###        * Year: 2001
###        * Publisher: Management Science, 47(8), 1113–1121
###        * Source: https://doi.org/10.1287/mnsc.47.8.1113.10226
###
###    Download the summary file "Summary_Experiment_3.pdf" or print on screen
###
#############################################################################

# Procedure to select the correct function to load the project data
def get_project_data(projectID):
    if projectID == 1:
        filename = Filefolder + "DS_Book_Table7_1.rcp" # Note: Optimal solution = 25
    elif projectID == 2:
        filename = Filefolder + "DS_Book_Table7_2.rcp" # Note: Optimal solution = 36
    elif projectID == 3:
        filename = Filefolder + "mv2.rcp" # Note: Optimal solution = 18 (Only MTS, LNRJ and LFT gives a relatively good solution (20) while the others are (much) worse)
    else:
        raise ValueError("Invalid projectID. Choose 1, 2, or 3.")
    return filename    

# Set the project ID (change this to 2 or 3 as needed)
projectID = 1
print_summary_file(Infofolder, 3)

###########################################################################################
### Step 1. Construct a CPM schedule and detect resource conflicts                      ###
###########################################################################################

# Read a project Patterson data file with single time/cost values (no trade-off)
  # Note 1: These projects only contain a successors_list so an empty predecessors_list must be given as parameter in "create_activity_network_dependencies"
  # Note 2: The Patterson file does not contain data for "time_cost_trade_offs" and "activity_risk_classes" but they are constructed during reading (with only one time/cost for each activity)
filename = get_project_data(projectID)
_, activity_set, successors_list, activity_names, \
        resource_requirements, resource_availability, _ = read_patterson_file(filename)

# Add dummy start and end nodes (Not necessary here (Patterson files have dummies) but good practice)
add_dummy_nodes_to_project_data(activity_set,activity_names,sul=successors_list,rr=resource_requirements)

activity_dependencies = create_activity_network_dependencies({},successors_list,activity_names, debugInfo = False)

# Construct the CPM schedule
graph, PD, BAC, planned_schedule = calculate_critical_path(activity_set, activity_dependencies, activity_names)
print('Planned duration (PD) = ', PD)
print('Budget at completion (BAC) = ', BAC)

# Visualize the network graph (created in the "calculate_critical_path" function)
visualize_network(graph, activity_names,showCP = True, showDummy = True, curvedEdges = True)

# Visualize the schedule using a Gantt chart
#show_gantt_chart(planned_schedule, showCP=False, showDummy=False, showCost=False, 
#                            xlabel_size = 25, ylabel_size = 25,
#                            xtick_size = 15, ytick_size = 15, title_size = 25)
show_gantt_chart(planned_schedule, showCP=True, showDummy=False, showCost=False)

# Visualise network and calculate the network topology indicators
visualize_network(graph, activity_names, showEdgeLabels=False, node_size=2000,showDummy = True, showCP = False, curvedEdges = True)
SP, AD, LA, TF = calculate_network_topology_indicators(activity_set, activity_dependencies, activity_names, writeOutput = True)



plot_resource_profiles(planned_schedule, resource_availability, resource_requirements, legend_size=12, showName = False)
plot_resource_profiles(planned_schedule, resource_availability, resource_requirements, legend_size=0, showName = False)
#plot_resource_profiles(planned_schedule, resource_availability, resource_requirements,
#                                        xlabel_size=15, ylabel_size=15, # Title of axes (Optional parameter)
#                                        xtick_size=15, ytick_size=15,   # Values of axes (")
#                                        legend_size=None,               # Font size of the legend (")
#                                        title_size=25
#                                 )

#raise SystemExit

####### TEST RESOURCE INDICATORS ######
###########################################################################################
### Step 2. Calculate the resource scarcity indicators.                                 ###
###########################################################################################

CPM_schedule = planned_schedule
RU, RF, RC, RS = calculate_resource_scarcity_indicators(
    CPM_schedule, 
    activity_set, resource_requirements, resource_availability,
    writeOutput = True)

#print("Resource Scarcity Indicators:")
#print(f"\tResource Use (RU): {RU:.2f}")
#print(f"\tResource Factor (RF): {RF:.2f}")
#print("\nResource Constrainedness (RC):\n" + "\n".join(f"\t{r}: {v:.2f}" for r, v in RC.items()))
#print("\nResource Strength (RS):\n" + "\n".join(f"\t{r}: {v:.2f}" for r, v in RS.items()))


###########################################################################################
### Step 3. Solve the resource-constrained project scheduling problem heuristically (priority rule based scheduling)
### --> Maybe use all the priority rules and generation schemes and forward/backward and construct a table with solutions?
###########################################################################################

priority_rules = ["SPT", "LPT", "MIS", "MTS", "LNRJ", "GRPW", "EST", "EFT", "LST", "LFT", "MSLK", "GRWC", "GCRWC"]

# Example experiment
priority_rule = "MIS"
priority_list = create_priority_list(priority_rule, activity_names, activity_set, activity_dependencies, resource_requirements, debugInfo = False)
print("Priority list = ", priority_list)
print("Activity set = ", activity_set)

#"""
# Find a resource feasible schedule with the priority list
project_makespan, project_cost, activity_schedule = serial_sgs(
    activity_names,
    activity_set,
    activity_dependencies,
    resource_requirements,
    resource_availability,
    priority_list,
    debugInfo = False
)

project_makespan, project_cost, activity_schedule, _, _ = parallel_sgs(activity_names, activity_set, activity_dependencies, resource_requirements, resource_availability, priority_list, debugInfo = False)

print("Project duration (makespan) = ", project_makespan)
print("Project cost (budget at completion) = ", project_cost)

# Print the activity_schedule 
for activity, schedule in activity_schedule.items():
    print(f"{activity}: {schedule}")

show_gantt_chart(activity_schedule)

plot_resource_profiles(activity_schedule, resource_availability, resource_requirements, showName = False)

###########################################################################################
### Step 4 Give the results for all priority rules
###         (e.g. Table 7.3 in the book for example project DS_Book_Table7_1.rcp)
### UNDER CONSTRUCTION: ALL priority rules/ S and P SGS / Li and Willis
###########################################################################################

for rule in priority_rules:
#    print(f"Processing priority rule: {rule}")
    print(f"Priority rule: {rule}", end="\t")
    priority_rule = rule
    priority_list = create_priority_list(priority_rule, activity_names, activity_set, activity_dependencies, resource_requirements, debugInfo = False)
    
    sorted_list = build_sorted_activities_by_predecessors(activity_set, activity_dependencies, priority_list)
#    print("sorted_list = ", sorted_list)
#    print(",".join(sorted_list), end="\t")
    
#    print(priority_list)
#    print(", ".join(str(value) for _, value in priority_list), end="\t")
    
    # Solve the problem with a serial schedule generation scheme (SSGS) (single forward run)
    project_makespan, _, activity_schedule = serial_sgs(activity_names, activity_set, activity_dependencies, resource_requirements, resource_availability, priority_list, debugInfo = False)

    print(project_makespan, end="\t")
#    plot_resource_profiles(activity_schedule, resource_availability, resource_requirements, legend_size=12, showName = False)
    
    # Use an iterative forward/backward approach using the SGSS (until no improvement found)
    
    # Solve the problem with a parallel schedule generation scheme (PSGS) (single forward run)
    project_makespan, total_cost, early_activity_schedule, late_activity_schedule, schedule_improvement = parallel_sgs(activity_names, activity_set, activity_dependencies, resource_requirements, resource_availability, priority_list, debugInfo = False)
    print(project_makespan)
#    plot_resource_profiles(early_activity_schedule, resource_availability, resource_requirements, legend_size=12, showName = False)    

    # Use an iterative forward/backward approach using the PGSS (until no improvement found)

    
### Note: THERE IS A PROBLEM WITH PSGS WITH GCRWC SINCE MY BOOK SAYS IT MUST BE 25

priority_rule = "GCRWC"
priority_list = create_priority_list(priority_rule, activity_names, activity_set, activity_dependencies, resource_requirements, debugInfo = False)
print(priority_list)
project_makespan, total_cost, early_activity_schedule, late_activity_schedule, schedule_improvement = parallel_sgs(activity_names, activity_set, activity_dependencies, 
                        resource_requirements, resource_availability, priority_list, debugInfo = False)
print(project_makespan)
plot_resource_profiles(early_activity_schedule, resource_availability, resource_requirements)
