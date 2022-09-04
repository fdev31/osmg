export function backToHome(sess, router) {
  sess.$reset();
  sess.save();
  router.push("/");
}
