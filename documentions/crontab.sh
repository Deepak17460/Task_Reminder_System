0 10 * * * /root/Task_Reminder_System/myvenv/bin/python3 /root/Task_Reminder_System/task_reminder_system/notify/notify.py >> /root/Task_Reminder_System/task_reminder_system/run_application/task_reminder_output_cron.log 2>&1
0 12 * * * /root/Task_Reminder_System/myvenv/bin/python3 /root/Task_Reminder_System/task_reminder_system/notify/notify.py >> /root/Task_Reminder_System/task_reminder_system/run_application/task_reminder_output_cron.log 2>&1
0 18 * * * /root/Task_Reminder_System/myvenv/bin/python3 /root/Task_Reminder_System/task_reminder_system/notify/notify.py >> /root/Task_Reminder_System/task_reminder_system/run_application/task_reminder_output_cron.log 2>&1




0 10 * * * /root/Task_Reminder_System/task_reminder_system/myvenv/bin/python3 /root/Task_Reminder_System/task_reminder_system/notify/notify.py >> /root/Task_Reminder_System/task_reminder_system/run_application/task_reminder_output_cronjob.log 2>&1
0 12 * * * /root/Task_Reminder_System/task_reminder_system/myvenv/bin/python3 /root/Task_Reminder_System/task_reminder_system/notify/notify.py >> /root/Task_Reminder_System/task_reminder_system/run_application/task_reminder_output_cronjob.log 2>&1
0 18 * * * /root/Task_Reminder_System/task_reminder_system/myvenv/bin/python3 /root/Task_Reminder_System/task_reminder_system/notify/notify.py >> /root/Task_Reminder_System/task_reminder_system/run_application/task_reminder_output_cronjob.log 2>&1



0 10 * * * /root/Task_Reminder_System/task_reminder_system/run_notify.sh >> /root/Task_Reminder_System/task_reminder_system/run_application/task_reminder_crontab.log 2>&1
0 12 * * * /root/Task_Reminder_System/task_reminder_system/run_notify.sh >> /root/Task_Reminder_System/task_reminder_system/run_application/task_reminder_crontab.log 2>&1
0 18 * * * /root/Task_Reminder_System/task_reminder_system/run_notify.sh >> /root/Task_Reminder_System/task_reminder_system/run_application/task_reminder_crontab.log 2>&1