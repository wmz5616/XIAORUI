<template>
    <div class="diagnosis-container">
        <div class="page-header">
            <h2>AI 智能学情诊断</h2>
            <p class="subtitle">精准定位知识漏洞，个性化定制提升方案</p>
        </div>

        <div v-if="step === 1" class="step-card fade-in">
            <el-card shadow="hover" class="config-card">
                <el-tabs v-model="activeMode" class="custom-tabs">
                    <el-tab-pane label="学科综合诊断" name="subject">
                        <el-form label-position="top">
                            <el-row :gutter="20">
                                <el-col :span="12">
                                    <el-form-item label="选择年级">
                                        <el-select v-model="config.grade" placeholder="请选择" size="large">
                                            <el-option-group label="高中">
                                                <el-option label="高一" value="高一" />
                                                <el-option label="高二" value="高二" />
                                                <el-option label="高三" value="高三" />
                                            </el-option-group>
                                            <el-option-group label="大学">
                                                <el-option label="大一" value="大一" />
                                                <el-option label="大二" value="大二" />
                                                <el-option label="大三" value="大三" />
                                                <el-option label="大四" value="大四" />
                                            </el-option-group>
                                        </el-select>
                                    </el-form-item>
                                </el-col>
                                <el-col :span="12">
                                    <el-form-item label="选择学科">
                                        <el-select v-model="config.subject" placeholder="请选择" size="large">
                                            <el-option v-for="sub in subjects" :key="sub" :label="sub" :value="sub" />
                                        </el-select>
                                    </el-form-item>
                                </el-col>
                            </el-row>
                        </el-form>
                    </el-tab-pane>

                    <el-tab-pane label="专项薄弱点攻克" name="topic">
                        <el-form label-position="top">
                            <el-form-item label="请输入你觉得困难的知识点">
                                <el-input v-model="config.topic" placeholder="例如：三角函数、牛顿第二定律、虚拟语气..." size="large"
                                    clearable>
                                    <template #prefix><el-icon>
                                            <Search />
                                        </el-icon></template>
                                </el-input>
                            </el-form-item>
                            <el-form-item label="选择年级（辅助AI判断难度）">
                                <el-select v-model="config.grade" placeholder="请选择" size="large" style="width: 100%">
                                    <el-option label="高一" value="高一" />
                                    <el-option label="高二" value="高二" />
                                    <el-option label="高三" value="高三" />
                                    <el-option label="大学阶段" value="大学" />
                                </el-select>
                            </el-form-item>
                        </el-form>
                    </el-tab-pane>
                </el-tabs>

                <div class="start-btn-wrapper">
                    <el-button type="primary" size="large" round class="start-btn" @click="startDiagnosis"
                        :loading="loading">
                        开始 AI 诊断
                        <el-icon class="el-icon--right">
                            <ArrowRight />
                        </el-icon>
                    </el-button>
                </div>
            </el-card>
        </div>

        <div v-if="step === 2" class="step-card slide-up">
            <el-card class="quiz-card">
                <template #header>
                    <div class="quiz-header">
                        <div class="quiz-meta">
                            <span class="subject-badge">{{ activeMode === 'subject' ? config.subject : config.topic
                                }}</span>
                            <span class="progress-text">进度: {{ currentQIndex + 1 }} / {{ questions.length }}</span>
                        </div>
                        <el-progress :percentage="((currentQIndex + 1) / questions.length) * 100" :show-text="false"
                            status="success" />
                    </div>
                </template>

                <div class="question-body">
                    <h3 class="q-text">{{ currentQuestion.content }}</h3>
                    <div class="options-group">
                        <div v-for="(opt, idx) in currentQuestion.options" :key="idx" class="option-item"
                            :class="{ selected: userAnswers[currentQIndex] === idx }" @click="selectAnswer(idx)">
                            <span class="opt-letter">{{ 'ABCD'[idx] }}</span>
                            <span class="opt-content">{{ opt }}</span>
                        </div>
                    </div>
                </div>

                <div class="quiz-footer">
                    <el-button v-if="currentQIndex > 0" @click="currentQIndex--" icon="ArrowLeft">上一题</el-button>
                    <div style="flex: 1"></div>
                    <el-button type="primary" v-if="currentQIndex < questions.length - 1" @click="currentQIndex++"
                        :disabled="userAnswers[currentQIndex] === undefined">
                        下一题 <el-icon class="el-icon--right">
                            <ArrowRight />
                        </el-icon>
                    </el-button>
                    <el-button type="success" v-else @click="submitDiagnosis" :loading="analyzing"
                        :disabled="userAnswers[currentQIndex] === undefined">
                        提交试卷 <el-icon class="el-icon--right">
                            <Check />
                        </el-icon>
                    </el-button>
                </div>
            </el-card>
        </div>

        <div v-if="step === 3" class="report-area fade-in">
            <el-row :gutter="24">
                <el-col :xs="24" :md="10">
                    <el-card shadow="never" class="score-card">
                        <div class="score-summary">
                            <el-progress type="dashboard" :percentage="scorePercent" :color="scoreColors">
                                <template #default>
                                    <span class="score-num">{{ correctCount }} / {{ questions.length }}</span>
                                    <div class="score-label">答对题数</div>
                                </template>
                            </el-progress>
                            <div class="result-tips">
                                <h3 v-if="wrongQuestions.length === 0" style="color: #67C23A">全对！太棒了！🎉</h3>
                                <h3 v-else style="color: #E6A23C">发现 {{ wrongQuestions.length }} 个知识盲区</h3>
                            </div>
                        </div>

                        <el-divider>错题解析</el-divider>

                        <div class="wrong-list">
                            <el-collapse accordion>
                                <el-collapse-item v-for="(wq, index) in wrongQuestions" :key="index" :name="index">
                                    <template #title>
                                        <span class="wrong-title">❌ 第 {{ wq.qIndex + 1 }} 题</span>
                                    </template>
                                    <div class="wrong-detail">
                                        <p class="w-q">{{ wq.question.content }}</p>
                                        <p class="w-ans error">你的答案: {{ 'ABCD'[wq.userAns] }}</p>
                                        <p class="w-ans success">正确答案: {{ 'ABCD'[Number(wq.question.answer)] }}</p>
                                    </div>
                                </el-collapse-item>
                            </el-collapse>
                            <div v-if="wrongQuestions.length === 0" class="perfect-state">
                                没有错题，继续保持！
                            </div>
                        </div>
                    </el-card>
                </el-col>

                <el-col :xs="24" :md="14">
                    <el-card shadow="hover" class="analysis-card">
                        <template #header>
                            <div class="card-header">
                                <span>🔍 AI 诊断出的薄弱点</span>
                                <el-tag type="danger" effect="dark">点击下方标签查看详解</el-tag>
                            </div>
                        </template>

                        <div v-if="weakPoints.length > 0" class="weak-points-cloud">
                            <p class="hint-text">AI 发现你在以下知识点存在漏洞，点击可生成专属学习方案：</p>
                            <div class="tags-wrapper">
                                <div v-for="(point, i) in weakPoints" :key="i" class="weak-tag"
                                    @click="analyzePoint(point)">
                                    <span class="tag-icon">⚡</span>
                                    <span class="tag-text">{{ point }}</span>
                                    <el-icon class="action-icon">
                                        <ArrowRight />
                                    </el-icon>
                                </div>
                            </div>
                        </div>
                        <el-empty v-else description="未发现明显薄弱点，请尝试更高难度的测试" />
                    </el-card>
                </el-col>
            </el-row>
        </div>

        <el-drawer v-model="drawerVisible" :title="'🤖 AI 深度解析: ' + currentAnalysisPoint" direction="rtl" size="50%"
            destroy-on-close>
            <div v-loading="analysisLoading" class="analysis-content">
                <div v-if="learningPath">
                    <el-alert title="AI 学习建议" type="success" :closable="false" show-icon style="margin-bottom: 20px;">
                        针对 <b>{{ currentAnalysisPoint }}</b>，我为你规划了以下提升路径：
                    </el-alert>

                    <el-timeline>
                        <el-timeline-item v-for="(step, index) in learningPath" :key="index"
                            :type="index === 0 ? 'primary' : ''" :color="index === 0 ? '#409EFF' : '#E4E7ED'"
                            size="large">
                            <h4 class="step-title">{{ step.title }}</h4>
                            <p class="step-desc">{{ step.desc }}</p>
                        </el-timeline-item>
                    </el-timeline>

                    <div class="drawer-footer">
                        <el-button type="primary" size="large"
                            @click="$router.push('/student/courses')">去学习相关课程</el-button>
                    </div>
                </div>
            </div>
        </el-drawer>

    </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Search, ArrowRight, ArrowLeft, Check, Warning } from '@element-plus/icons-vue'

const subjects = ['Python', '数学', '物理', '英语', '历史', '化学']
const activeMode = ref('subject')
const step = ref(1)
const loading = ref(false)
const analyzing = ref(false)
const config = reactive({ grade: '高一', subject: '数学', topic: '' })
const questions = ref([])
const currentQIndex = ref(0)
const userAnswers = ref([])
const currentQuestion = computed(() => questions.value[currentQIndex.value] || {})
const wrongQuestions = ref([])
const correctCount = ref(0)
const scorePercent = computed(() => questions.value.length ? (correctCount.value / questions.value.length) * 100 : 0)
const scoreColors = [
    { color: '#F56C6C', percentage: 40 },
    { color: '#E6A23C', percentage: 70 },
    { color: '#67C23A', percentage: 100 },
]
const weakPoints = ref([])
const drawerVisible = ref(false)
const currentAnalysisPoint = ref('')
const analysisLoading = ref(false)
const learningPath = ref(null)

const startDiagnosis = async () => {
    if (activeMode.value === 'topic' && !config.topic) return ElMessage.warning("请输入薄弱知识点")

    loading.value = true
    try {
        const token = localStorage.getItem('token')
        const payload = {
            mode: activeMode.value,
            grade: config.grade,
            subject: config.subject,
            topic: activeMode.value === 'topic' ? config.topic : null
        }

        const res = await axios.post('http://localhost:8000/ai-engine/diagnostic/start', payload, {
            headers: { Authorization: `Bearer ${token}` }
        })

        if (res.data && res.data.length > 0) {
            questions.value = res.data
        } else {
            questions.value = [
                { content: `【演示】关于${payload.topic || payload.subject}的基础概念，下列说法正确的是？`, options: ["选项A", "选项B", "选项C", "选项D"], answer: 0 },
                { content: "【演示】这道题测试你的进阶理解能力。", options: ["答案是A", "答案是B", "答案是C", "答案是D"], answer: 2 }
            ]
            ElMessage.warning("使用演示题目")
        }

        step.value = 2
        currentQIndex.value = 0
        userAnswers.value = new Array(questions.value.length)
    } catch (e) {
        ElMessage.error("生成试卷失败")
    } finally {
        loading.value = false
    }
}

const selectAnswer = (idx) => {
    userAnswers.value[currentQIndex.value] = idx
}

const submitDiagnosis = async () => {
    analyzing.value = true
    wrongQuestions.value = []
    correctCount.value = 0

    questions.value.forEach((q, idx) => {
        const userAns = userAnswers.value[idx]
        const correctAns = Number(q.answer)

        if (userAns === correctAns) {
            correctCount.value++
        } else {
            wrongQuestions.value.push({
                qIndex: idx,
                question: q,
                userAns: userAns
            })
        }
    })
    try {
        const token = localStorage.getItem('token')
        if (wrongQuestions.value.length > 0) {
            const res = await axios.post('http://localhost:8000/ai-engine/diagnostic/analyze',
                { wrong_questions: wrongQuestions.value.map(wq => wq.question) },
                { headers: { Authorization: `Bearer ${token}` } }
            )
            weakPoints.value = res.data.weak_points || []
        } else {
            weakPoints.value = []
        }
        step.value = 3
    } catch (e) {
        ElMessage.error("分析失败")
    } finally {
        analyzing.value = false
    }
}
const analyzePoint = async (point) => {
    currentAnalysisPoint.value = point
    drawerVisible.value = true
    analysisLoading.value = true
    learningPath.value = null

    try {
        const token = localStorage.getItem('token')
        const res = await axios.post('http://localhost:8000/ai-engine/learning-path',
            {
                name: "Student",
                grade: config.grade,
                weak_subjects: [point]
            },
            { headers: { Authorization: `Bearer ${token}` } }
        )
        if (res.data.path) learningPath.value = res.data.path
        else if (Array.isArray(res.data)) learningPath.value = res.data
        else {
            learningPath.value = [
                { title: "概念回顾", desc: `重新复习 ${point} 的定义和基本性质。` },
                { title: "强化练习", desc: "完成相关专项练习题 3 组。" },
                { title: "总结反思", desc: "整理错题本，举一反三。" }
            ]
        }
    } catch (e) {
        ElMessage.error("获取学习建议失败")
    } finally {
        analysisLoading.value = false
    }
}
</script>

<style scoped>
.diagnosis-container {
    max-width: 1000px;
    margin: 20px auto;
    padding: 20px;
    font-family: 'PingFang SC', sans-serif;
}

.page-header {
    text-align: center;
    margin-bottom: 40px;
}

.page-header h2 {
    font-size: 28px;
    color: #303133;
    margin-bottom: 10px;
}

.subtitle {
    color: #909399;
    font-size: 14px;
}

.step-card {
    max-width: 800px;
    margin: 0 auto;
}

.config-card {
    border-radius: 12px;
    padding: 20px;
}

.custom-tabs :deep(.el-tabs__item) {
    font-size: 16px;
    height: 50px;
}

.start-btn-wrapper {
    text-align: center;
    margin-top: 40px;
}

.start-btn {
    width: 200px;
    height: 50px;
    font-size: 18px;
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

.quiz-card {
    border-radius: 12px;
}

.quiz-header {
    margin-bottom: 10px;
}

.quiz-meta {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    color: #606266;
}

.subject-badge {
    background: #ecf5ff;
    color: #409EFF;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: bold;
}

.q-text {
    font-size: 18px;
    margin: 30px 0;
    line-height: 1.6;
}

.option-item {
    display: flex;
    align-items: center;
    padding: 15px;
    margin-bottom: 15px;
    border: 1px solid #dcdfe6;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
}

.option-item:hover {
    border-color: #409EFF;
    background: #f9fafc;
}

.option-item.selected {
    border-color: #409EFF;
    background: #ecf5ff;
}

.opt-letter {
    width: 32px;
    height: 32px;
    background: #f0f2f5;
    border-radius: 50%;
    text-align: center;
    line-height: 32px;
    margin-right: 15px;
    font-weight: bold;
    color: #606266;
}

.selected .opt-letter {
    background: #409EFF;
    color: white;
}

.quiz-footer {
    margin-top: 40px;
    display: flex;
}

/* 阶段 3: 报告 */
.score-card {
    text-align: center;
    padding: 20px;
    height: 100%;
    border-radius: 12px;
}

.score-summary {
    margin-bottom: 30px;
}

.score-num {
    font-size: 24px;
    font-weight: bold;
    display: block;
}

.score-label {
    font-size: 12px;
    color: #909399;
}

.result-tips {
    margin-top: 15px;
}

.wrong-list {
    text-align: left;
    margin-top: 20px;
}

.wrong-title {
    font-weight: bold;
    color: #F56C6C;
}

.wrong-detail {
    padding: 10px;
    background: #fef0f0;
    border-radius: 4px;
    font-size: 14px;
}

.w-q {
    margin-bottom: 8px;
    color: #303133;
}

.w-ans.error {
    color: #F56C6C;
}

.w-ans.success {
    color: #67C23A;
    font-weight: bold;
}

.perfect-state {
    text-align: center;
    color: #67C23A;
    padding: 20px;
    background: #f0f9eb;
    border-radius: 8px;
}

.analysis-card {
    height: 100%;
    border-radius: 12px;
    border: 1px solid #e4e7ed;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.hint-text {
    color: #606266;
    margin-bottom: 20px;
}

.tags-wrapper {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
}

.weak-tag {
    background: #fff;
    border: 1px solid #fde2e2;
    border-radius: 50px;
    padding: 10px 20px;
    color: #F56C6C;
    cursor: pointer;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 8px rgba(245, 108, 108, 0.1);
    transition: all 0.3s;
}

.weak-tag:hover {
    background: #fef0f0;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(245, 108, 108, 0.2);
}

.tag-icon {
    margin-right: 8px;
}

.tag-text {
    font-weight: bold;
    font-size: 15px;
}

.action-icon {
    margin-left: 10px;
    opacity: 0.6;
}

/* 动画 */
.fade-in {
    animation: fadeIn 0.6s ease;
}

.slide-up {
    animation: slideUp 0.5s ease;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.analysis-content {
    padding: 10px;
}

.step-title {
    margin: 0 0 5px 0;
    color: #303133;
}

.step-desc {
    margin: 0;
    color: #606266;
    line-height: 1.5;
}

.drawer-footer {
    margin-top: 40px;
    text-align: center;
}
</style>