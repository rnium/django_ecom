if(isAuthenticated=="True" & is_shipping_able=="False") {
    document.getElementById('form-wrapper').classList.add('hidden')
    document.getElementById('payment-info').classList.remove('hidden')
}

let  form = document.getElementById('form')
form.addEventListener('submit', event => {
    event.preventDefault()
    document.getElementById('form-button').classList.add('hidden')
    document.getElementById('payment-info').classList.remove('hidden')
})


