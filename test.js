const load = (name) =>
{
    console.log(data[name])
    console.log(data.person[0])
    const page = data.person.filter(p =>  p.firstName === name)
    console.log(page)
}

const data= {
    "person": [
        {
            "firstName": "Clark",
            "lastName": "Kent",
            "job": "Reporter",
            "roll": 20
        },
        {
            "firstName": "Bruce",
            "lastName": "Wayne",
            "job": "Playboy",
            "roll": 30
        },
        {
            "firstName": "Peter",
            "lastName": "Parker",
            "job": "Photographer",
            "roll": 40
        }
    ]
 }
load('Peter')