document.addEventListener("DOMContentLoaded", (event) => {
  const checkboxes = document.querySelectorAll(
    '.field-is_main input[type="checkbox"]'
  );
  let isFirstCheckbox = true;

  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", (event) => {
      if (event.target.checked) {
        checkboxes.forEach((otherCheckbox) => {
          if (otherCheckbox !== event.target) {
            otherCheckbox.checked = false;
          }
        });
      }
    });

    // Set the first checkbox as checked and others as unchecked
    if (isFirstCheckbox) {
      checkbox.checked = true;
      isFirstCheckbox = false;
    } else {
      checkbox.checked = false;
    }
  });
});