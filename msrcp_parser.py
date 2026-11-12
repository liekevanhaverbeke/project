import os


def read_msrcp_file(filepath):
    """Reads an .msrcp file from MSLIB3/MSLIB4 and converts it into data structures

    directly compatible with ProPy (Experiment 3).
    """
    with open(filepath, 'r') as f:
        # Read all non-empty lines and strip whitespace
        raw_lines = [line.strip() for line in f if line.strip()]

    # Helper logic to split sections based on \* Module *\ headers
    modules = {}
    current_module = None
    for line in raw_lines:
        if line.startswith('\\*') and line.endswith('*\\'):
            current_module = line.strip('\\* ').strip()
            modules[current_module] = []
        elif current_module is not None:
            modules[current_module].append(line)

    # ---------------------------------------------------------
    # 1. PROJECT MODULE (Network & Durations)
    # ---------------------------------------------------------
    proj_lines = modules['Project Module']
    header = list(map(int, proj_lines[0].split()))
    num_activities = header[0]  # Including dummy start (1) and dummy end (N)
    num_resources = header[1]
    num_skills = header[2]
    num_skill_levels = header[3]

    best_known_makespan = int(proj_lines[1])
    deadline = int(proj_lines[2])

    activity_set = {}
    successors_list = {}
    activity_names = {}

    # Activities start at line index 3 of the Project Module
    for idx in range(num_activities):
        act_id = idx + 1  # 1-based IDs as in Patterson/MSRCP format
        parts = list(map(int, proj_lines[3 + idx].split()))

        duration = parts[0]
        num_succ = parts[1]
        succs = parts[2 : 2 + num_succ] if num_succ > 0 else []

        activity_set[act_id] = {
            'duration': duration,
            'cost': 0.0,
        }
        successors_list[act_id] = succs
        activity_names[act_id] = f'A{act_id}'

    # ---------------------------------------------------------
    # 2. WORKFORCE MODULE (Staff Profiles & Primary Skills)
    # ---------------------------------------------------------
    wf_lines = modules['Workforce Module']
    workforce_skills = [
        list(map(int, line.split())) for line in wf_lines[:num_resources]
    ]

    wf_level_lines = modules.get('Workforce Module with Skill Levels', [])
    workforce_levels = [
        list(map(int, line.split())) for line in wf_level_lines[:num_resources]
    ]

    # Determine primary skill per resource (for Strategy A)
    # Rule: highest skill level; in case of a tie, pick the first skill (lowest index)
    primary_skills = {}
    resource_availability_strat_A = [0] * num_skills

    for r_idx in range(num_resources):
        if workforce_levels:
            levels = workforce_levels[r_idx]
            best_skill = max(range(num_skills), key=lambda s: levels[s])
        else:
            skills = workforce_skills[r_idx]
            best_skill = skills.index(1)

        primary_skills[r_idx + 1] = best_skill + 1  # 1-based skill ID
        resource_availability_strat_A[best_skill] += 1

    # Total maximum capacity per skill (Strategy B multi-skilled pool)
    max_skill_pool = [
        sum(workforce_skills[r][s] for r in range(num_resources))
        for s in range(num_skills)
    ]

    # ---------------------------------------------------------
    # 3. SKILL REQUIREMENTS MODULE (Activity Requirements)
    # ---------------------------------------------------------
    req_lines = modules['Skill Requirements Module']
    resource_requirements = {}

    for idx in range(num_activities):
        act_id = idx + 1
        reqs = list(map(int, req_lines[idx].split()))
        resource_requirements[act_id] = reqs

    # ---------------------------------------------------------
    # 4. COST MODULE (Optional for break-even and cost analysis)
    # ---------------------------------------------------------
    cost_data = {}
    if 'Cost Module' in modules:
        c_lines = modules['Cost Module']
        fixed_min, var_min = map(float, c_lines[0].split())
        fixed_skill_costs = [
            list(map(float, line.split()))
            for line in c_lines[1 : 1 + num_skills]
        ]
        var_skill_costs = [
            list(map(float, line.split()))
            for line in c_lines[1 + num_skills : 1 + 2 * num_skills]
        ]
        cost_data = {
            'fixed_min': fixed_min,
            'var_min': var_min,
            'fixed_skill_costs': fixed_skill_costs,
            'var_skill_costs': var_skill_costs,
        }

    # Bundle all extra multi-skill data for Strategy B and SRA
    ms_data = {
        'num_resources': num_resources,
        'num_skills': num_skills,
        'num_skill_levels': num_skill_levels,
        'best_known_makespan': best_known_makespan,
        'deadline': deadline,
        'workforce_skills': workforce_skills,
        'workforce_levels': workforce_levels,
        'primary_skills': primary_skills,
        'max_skill_pool': max_skill_pool,
        'cost_data': cost_data,
    }

    return (
        filepath,
        activity_set,
        successors_list,
        activity_names,
        resource_requirements,
        resource_availability_strat_A,
        ms_data,
    )


# =========================================================================
# TEST BLOCK: Runs automatically when you execute msrcp_parser.py directly
# =========================================================================
if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mslib4_folder = os.path.join(base_dir, 'MSLIB4')

    # Collect all .msrcp files (including subdirectories)
    all_files = []
    for root, dirs, files in os.walk(mslib4_folder):
        for file in files:
            if file.endswith('.msrcp'):
                all_files.append(os.path.join(root, file))

    # Sort naturally by filename length and name so Set4_1 comes before Set4_10
    all_files = sorted(
        all_files,
        key=lambda p: (len(os.path.basename(p)), os.path.basename(p)),
    )

    if len(all_files) == 0:
        print(f'No .msrcp files found in {mslib4_folder}. Check folder path!')
    else:
        first_10 = all_files[:10]
        last_10 = all_files[-10:]

        def print_batch(batch_name, file_list):
            print(f"\n{'='*85}")
            print(f' {batch_name} ({len(file_list)} files)')
            print(f"{'='*85}")
            for idx, filepath in enumerate(file_list, start=1):
                fname = os.path.basename(filepath)
                try:
                    (
                        _,
                        act_set,
                        succ_list,
                        act_names,
                        res_req,
                        res_avail_A,
                        ms_data,
                    ) = read_msrcp_file(filepath)

                    real_acts = len(act_set) - 2  # Exclude start & end dummy
                    print(
                        f'[{idx:02d}] {fname:<22} -> OK | '
                        f'{real_acts} tasks (+2 dummies) | '
                        f"{ms_data['num_resources']} workers | "
                        f'Primary skills (Strat A): {res_avail_A} vs. Multi-skilled pool (Strat B): {ms_data["max_skill_pool"]}'
                    )
                except Exception as e:
                    print(f'[{idx:02d}] {fname:<22} -> FAILED | Error: {e}')

        # 1. Print detailed output for first 10 and last 10
        print_batch('FIRST 10 PROJECTS (MSLIB4)', first_10)
        print_batch('LAST 10 PROJECTS (MSLIB4)', last_10)

        # 2. Validate ALL files in the folder silently to get the exact total
        total_passed = 0
        failed_files = []
        for filepath in all_files:
            try:
                (
                    _,
                    act_set,
                    succ_list,
                    act_names,
                    res_req,
                    res_avail_A,
                    ms_data,
                ) = read_msrcp_file(filepath)

                assert len(act_set) > 0, 'Empty activity set'
                assert (
                    len(act_set) == len(succ_list) == len(res_req)
                ), 'Module length mismatch'
                assert (
                    sum(res_avail_A) == ms_data['num_resources']
                ), 'Primary skill count != total workforce'

                total_passed += 1
            except Exception as e:
                failed_files.append((os.path.basename(filepath), str(e)))

        # 3. Print overall status with exact total
        print('\n' + '=' * 85)
        print(
            f'OVERALL PARSER STATUS: {total_passed}/{len(all_files)} total projects in MSLIB4 parsed and validated successfully!'
        )
        if failed_files:
            print(
                f'FAILED FILES ({len(failed_files)}): {[f[0] for f in failed_files]}'
            )
        print('=' * 85)