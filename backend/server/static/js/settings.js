function dates_menu() {
  return document.getElementById("dates_menu");
}

function weeks_menu() {
  return document.getElementById("weeks_menu");
}

function enable_submission_check() {
  let inputs = [
    document.getElementById("start_date"),
    document.getElementById("end_date"),
    document.getElementById("weeks")
  ];
  let menus = [
    document.getElementById("dates_menu"),
    document.getElementById("weeks_menu")
  ];
  let radios = document.getElementsByClassName("radio");

  function submit_helper() {
    for (let index = 0; index < radios.length; index++) {
      if (radios[index].checked === false) {
        continue;
      }
      switch (radios[index].id) {
        case "selection_date":
          let start_date = document.getElementById("start_date");
          let end_date = document.getElementById("end_date");
          document.getElementById("submit_button").disabled =
            start_date.value === "" || end_date.value === "";
          break;
        case "selection_weeks":
          let weeks = document.getElementById("weeks");
          document.getElementById("submit_button").disabled =
            weeks.value === "";
          break;
        default:
          console.log("Unknown radio");
          break;
      }
    }
  }

  for (let i = 0; i < inputs.length; i++) {
    inputs[i].addEventListener("change", function() {
      submit_helper();
    });
  }
  for (let i = 0; i < menus.length; i++) {
    menus[i].addEventListener("click", function() {
      submit_helper();
    });
  }
}

function open_menu(selected_menu, other_menus) {
  if (selected_menu.querySelector(".radio").checked === true) {
    return;
  }
  if (other_menus.querySelector(".radio").checked === true) {
    other_menus.querySelector(".radio").checked = false;
    other_menus.querySelector(".settings").hidden = true;
  }
  selected_menu.querySelector(".radio").checked = true;
  selected_menu.querySelector(".settings").hidden = false;
}

dates_menu().querySelector(".radio").checked = false;
weeks_menu().querySelector(".radio").checked = false;

dates_menu().addEventListener("click", () =>
  open_menu(dates_menu(), weeks_menu())
);
weeks_menu().addEventListener("click", () =>
  open_menu(weeks_menu(), dates_menu())
);
enable_submission_check();
