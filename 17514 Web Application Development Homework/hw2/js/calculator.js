let stack = [0]
let entering=true
const WARNING = "#dc143c";
const FREEPUSH = "#fff8dc";
const OPERATE = "#3cb371";

function init(value) {
    document.getElementById("output").innerHTML = value;
    stack = [0];
    entering = true;
}

function onClickDigit(number) {
    if (entering) {
        prev = stack.pop()
        stack.push(prev * 10 + number);    
    } else {
        stack.push(number);
        entering = true;
    } 
    updateOutputArea();
    document.getElementById("output").style.background = FREEPUSH;
}


function onClickOperation(oper) {   
    console.log(stack);
    if (oper === "put") {
        if (stack.length === 3) {            
            errorHandler("OF");            
            return;
        } 
        stack.push(0);
        document.getElementById("output").style.background = FREEPUSH;
    } else {
        if (stack.length === 1) {
            errorHandler("UF");
            return;
        } else {
            const x = stack.pop();
            const y = stack.pop();
            if (x === 0) {
                errorHandler("DZ");                
                return;
            }
            calculate(y, x, oper);                
        }
    }    
    updateOutputArea();
}
    

function calculate(x, y, oper) {
    switch(oper) {
        case "+":
            stack.push(x + y);
            break;
        case "-":
            stack.push(x - y);
            break;
        case "*":
            stack.push(x * y);
            break;
        case "/":            
            stack.push(parseInt(x / y));
            break;
        default: 
            console.log("error");
            break;
    }
    entering = false;           
    document.getElementById("output").style.background = OPERATE;
}


function errorHandler(error) {
    switch (error) {
        case "UF":
            init("stack underflow");
            break;
        case "OF":
            init("stack overflow");
            break;
        case "DZ":            
            init("divide by zero");
            break;
        default:
            break;
    }    
    document.getElementById("output").style.background = WARNING;    
    entering = true;
}

function updateOutputArea() {    
    document.getElementById("output").innerHTML = stack[stack.length-1];
}