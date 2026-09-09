const user = {
    name: "Alice",
    role: "Developer",
};

function describeUser(user) {
    return `${user.name} is a ${user.role}.`;
}

console.log(describeUser(user));
