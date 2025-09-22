.PHONY: load-auth load-comments-get load-comments-post load-keywords-get load-tasks load-morphological

load-auth:
	vegeta attack -duration=60s -rate=1000 -targets=loadtests/auth_login.targets | vegeta report

load-comments-get:
	vegeta attack -duration=60s -rate=1000 -targets=loadtests/comments_get.targets | vegeta report

load-comments-post:
	vegeta attack -duration=60s -rate=1000 -targets=loadtests/comments_post.targets | vegeta report

load-keywords-get:
	vegeta attack -duration=60s -rate=1000 -targets=loadtests/keywords_get.targets | vegeta report

load-tasks:
	vegeta attack -duration=60s -rate=1000 -targets=loadtests/tasks_enqueue.targets | vegeta report

load-morphological:
	vegeta attack -duration=60s -rate=1000 -targets=loadtests/morphological_analyze.targets | vegeta report