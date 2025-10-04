const subscriptions = [
    {
        id:1,
        name:"Free Explorer",
        price: 0,
        features:[
            'Access to personalized travel recommendations.',
            'Save destinations in your Saved List.',
            'Ad-supported experience.',
            'Basic AI-generated trip itineraries.'
        ],
        isCurrentPlan:true,
        isPopular:false,
    },
    {
        id:2,
        name: "Premium Adventurer",
        price: 499.99,
        features:[
            'Ad-free experience.',
            'Enhanced AI-generated trip itineraries.',
            'Exclusive access to articles.'

        ],
        isCurrentPlan:false,
        isPopular:false,
    },
    
]

export default subscriptions;