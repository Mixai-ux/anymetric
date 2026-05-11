export async function onRequest({ request, next }) {
  const ua = request.headers.get('User-Agent') || '';
  const isBot = /Googlebot|bingbot|Slurp|DuckDuckBot|Baiduspider|YandexBot|facebot|ia_archiver/i.test(ua);
  const resp = await next();
  if (isBot) return resp;
  const country = request.headers.get('CF-IPCountry') || '';
  if (!country) return resp;
  const r = new Response(resp.body, resp);
  r.headers.append('Set-Cookie', `am_country=${country}; Path=/; Max-Age=86400; SameSite=Lax`);
  return r;
}
