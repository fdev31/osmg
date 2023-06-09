import { createRouter, createWebHistory } from "vue-router";
import HomeView from "@/views/HomeView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/r/:session",
      name: "join",
      component: HomeView,
    },
    {
      path: "/lobby",
      name: "lobby",
      component: () => import("@/views/LobbyView.vue"),
    },
    {
      path: "/scoreboard",
      name: "scoreboard",
      component: () => import("@/views/ScoreBoard.vue"),
    },
    {
      path: "/game-atakks",
      name: "atakks",
      component: () => import("@/views/GameAtakks.vue"),
    },
    {
      path: "/game-marathon",
      name: "marathon",
      component: () => import("@/views/GameMarathon.vue"),
    },
    {
      path: "/about",
      name: "about",
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import("@/views/AboutView.vue"),
    },
  ],
});

export default router;
