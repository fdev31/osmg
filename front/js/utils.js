async function getJson(url) {
  const req = await fetch(url);
  const data = await req.json();
  return data;
}