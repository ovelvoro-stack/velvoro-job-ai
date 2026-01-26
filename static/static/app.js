function loadQuestions() {
    const role = document.getElementById("role").value;

    if (role === "IT") {
        q1.innerText = "Explain your IT skills";
        q2.innerText = "What programming languages do you know?";
    } 
    else if (role === "Pharma") {
        q1.innerText = "Explain your pharma experience";
        q2.innerText = "What regulations do you know?";
    } 
    else {
        q1.innerText = "Explain your work experience";
        q2.innerText = "Why should we hire you?";
    }
}
