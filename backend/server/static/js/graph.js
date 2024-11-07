exercise_info = () => {
    console.log("Getting information")
    return JSON.parse(
        document.getElementById("exercise_info").value
    )

}
category_query = () => {
    let x = document.getElementById("categories")
    x.addEventListener("change", onMuscleGroupChange)
    return x
}

exercise_query = () => {
    let x = document.getElementById("exercises")
    x.addEventListener("change", onExercisesChange)
    return x
}
category_query()
exercise_query()

function createOption(select_element, text, value) {
    let new_option = document.createElement('option');
    new_option.text = text;
    new_option.value = value;
    select_element.add(new_option);
}

function onMuscleGroupChange() {
    let categories_select = document.getElementById("categories");
    let reps_ranges_select = document.getElementById("rep_ranges");
    console.log("Muscle group changing...")
    changeExerciseOptions(categories_select.selectedOptions[0].label)
    reps_ranges_select.replaceChildren();
}

function onExercisesChange() {
    let exercise_name_select = document.getElementById("exercises");
    console.log("Exercise changing...")
    changeRepsOptions(exercise_name_select.selectedOptions[0].label)
}

function changeExerciseOptions(category) {
    let exercise_name_select = document.getElementById("exercises");
    let exercise_info_dict = exercise_info

    exercise_name_select.replaceChildren();
    exercise_name_select.setAttribute('style', "visibility: visible;")
    createOption(exercise_name_select, "", "");

    for (let exercise_name in exercise_info_dict) {
        let display_name = exercise_name.replaceAll("_", " ").toUpperCase();
        if (exercise_info_dict[exercise_name]['category'] === category) {
            createOption(exercise_name_select, display_name, exercise_name);
        }
    }
    console.log("Exercise changing...")
}

function changeRepsOptions(exercise_name) {
    let selected = exercise_name.toUpperCase().replaceAll(" ", "_");
    let reps_ranges_select = document.getElementById("rep_ranges");
    let exercise_info_dict = exercise_info

    reps_ranges_select.replaceChildren();
    reps_ranges_select.setAttribute('style', "visibility: visible;")
    let new_rep_ranges = exercise_info_dict[selected]['rep_ranges'];
    createOption(reps_ranges_select, "No Filter", "None")

    for (let i = 0; i < new_rep_ranges.length; i++) {
        createOption(reps_ranges_select, new_rep_ranges[i], new_rep_ranges[i]);
    }
    console.log("Reps changing...")
}
