document.getElementById('searchBtn').addEventListener('click', () => {
  const username = document.getElementById('githubSearch').value.trim();
  if (username === '') {
    alert('Пожалуйста, введите имя пользователя GitHub.');
    return;
  }
  fetchUser(username);
});

function fetchUser(username) {
  fetch(`https://api.github.com/users/${username}`)
    .then(res => {
      if (!res.ok) {
        throw new Error(`Ошибка: ${res.status} ${res.statusText}`);
      }
      return res.json();
    })
    .then(user => {
      displayUser(user);
    })
    .catch(error => {
      // Обработка ошибок сети или API
      alert(`Произошла ошибка: ${error.message}\nПожалуйста, попробуйте позже или проверьте соединение.`);
      document.getElementById('results').innerHTML = '';
    });
}