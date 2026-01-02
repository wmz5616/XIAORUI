import { createRouter, createWebHistory } from "vue-router";
import Login from "../views/Login.vue";
import StudentDashboard from "../views/student/Dashboard.vue";
import TeacherDashboard from "../views/teacher/Dashboard.vue";
import AdminDashboard from "../views/admin/Dashboard.vue";
import StudyRoom from "../views/student/StudyRoom.vue";
import Quiz from "../views/student/Quiz.vue";
import StudentProfile from "../views/student/Profile.vue";
import Forum from "../views/student/Forum.vue";
import HomeworkList from "../views/student/HomeworkList.vue";
import AiDiagnosis from "../views/student/AiDiagnosis.vue";
import MyCourses from "../views/student/MyCourses.vue";
import KnowledgeGraph from "../views/student/KnowledgeGraph.vue";
import { jwtDecode } from "jwt-decode";

const routes = [
  {
    path: "/",
    redirect: "/login",
  },
  {
    path: "/login",
    name: "Login",
    component: Login,
  },
  {
    path: "/student",
    name: "StudentDashboard",
    component: StudentDashboard,
    meta: { requiresAuth: true, role: "student" },
  },
  {
    path: "/student/courses",
    name: "MyCourses",
    component: MyCourses,
    meta: { requiresAuth: true, role: "student" },
  },
  {
    path: "/student/knowledge-graph/:courseId",
    name: "KnowledgeGraph",
    component: KnowledgeGraph,
    meta: { requiresAuth: true, role: "student" },
  },
  {
    path: "/study/:id",
    name: "StudyRoom",
    component: StudyRoom,
    meta: { requiresAuth: true, role: "student" },
  },
  {
    path: "/quiz/:id",
    name: "Quiz",
    component: Quiz,
    meta: { requiresAuth: true, role: "student" },
  },
  {
    path: "/student/profile",
    name: "StudentProfile",
    component: StudentProfile,
    meta: { requiresAuth: true, role: "student" },
  },
  {
    path: "/student/forum",
    name: "StudentForum",
    component: Forum,
    meta: { requiresAuth: true, role: "student" },
  },
  {
    path: "/student/homework-list",
    name: "HomeworkList",
    component: HomeworkList,
    meta: { requiresAuth: true, role: "student" },
  },
  {
    path: "/student/ai-diagnosis",
    name: "AiDiagnosis",
    component: AiDiagnosis,
    meta: { requiresAuth: true, role: "student" },
  },
  {
    path: "/teacher",
    name: "TeacherDashboard",
    component: TeacherDashboard,
    meta: { requiresAuth: true, role: "teacher" },
  },
  {
    path: "/admin",
    name: "AdminDashboard",
    component: AdminDashboard,
    meta: { requiresAuth: true, role: "admin" },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");

  if (to.meta.requiresAuth) {
    if (!token) {
      next("/login");
    } else {
      try {
        const decoded = jwtDecode(token);
        if (to.meta.role && decoded.role !== to.meta.role) {
          if (decoded.role === "student") next("/student");
          else if (decoded.role === "teacher") next("/teacher");
          else if (decoded.role === "admin") next("/admin");
          else next("/login");
        } else {
          next();
        }
      } catch (e) {
        localStorage.removeItem("token");
        next("/login");
      }
    }
  } else {
    next();
  }
});

export default router;