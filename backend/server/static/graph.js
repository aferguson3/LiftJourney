let categories_select = document.getElementById("categories");
let exercise_name_select = document.getElementById("exercises");
let reps_ranges_select = document.getElementById("rep_ranges");
let exercise_info_dict = {{ exercise_info | tojson }};



function onCategoriesChange(event) {
  console.log(event)
  changeExerciseOptions(categories_select.selectedOptions[0].label)
}

function onExercisesChange(event) {
  changeRepsOptions(exercise_name_select.selectedOptions[0].label)
}

function createOption(select_element, text, value) {
  let new_option = document.createElement('option');
    new_option.text = text;
    new_option.value = value;
    select_element.add(new_option);
}
function changeExerciseOptions(category){
  exercise_name_select.replaceChildren();
  exercise_name_select.setAttribute('style', "visibility: visible;")
  createOption(exercise_name_select,"-- Select a Category --", "");
    for (var exercise_name in exercise_info_dict) {
      let display_name = exercise_name.replaceAll("_", " ").toUpperCase();
      if (exercise_info_dict[exercise_name]['category'] == category){
        createOption(exercise_name_select, display_name, exercise_name);
      }
    }
}
function changeRepsOptions(exercise_name) {
  let selected = exercise_name.toUpperCase().replaceAll(" ", "_");
  let length = reps_ranges_select.options.length;
  reps_ranges_select.replaceChildren();
  reps_ranges_select.setAttribute('style', "visibility: visible;")
  let new_rep_ranges = exercise_info_dict[selected]['rep_ranges'];
  
  for (let i=0; i < new_rep_ranges.length; i++){
    if (i == 0) {
      createOption(reps_ranges_select,"No Filter", "None");
    }
    createOption(reps_ranges_select,new_rep_ranges[i],new_rep_ranges[i]);
  }
}