import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import StudentDashboard from '../views/student/Dashboard.vue'
import KnowledgeGraph from '../views/student/KnowledgeGraph.vue'
import TeacherDashboard from '../views/teacher/Dashboard.vue'
import AdminDashboard from '../views/admin/Dashboard.vue'
import Forum from '../views/student/Forum.vue'
import StudyRoom from '../views/student/StudyRoom.vue'
import Profile from '../views/student/Profile.vue'
import Quiz from '../views/student/Quiz.vue'
import DiagnosticTest from '../views/student/DiagnosticTest.vue'

const routes = [
  { path: '/', component: Login },
  
  { path: '/student', component: StudentDashboard },
  { path: '/student/graph', component: KnowledgeGraph },
  { path: '/forum', component: Forum },
  { path: '/learn/:id', component: StudyRoom },
  { path: '/student/profile', component: Profile },
  { path: '/quiz/:id', component: Quiz },
  { path: '/student/diagnostic', component: DiagnosticTest },

  { path: '/teacher', component: TeacherDashboard },

  { path: '/admin', component: AdminDashboard }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router