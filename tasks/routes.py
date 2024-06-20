from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, Task
from tasks import tasks_bp
from forms import TaskForm

@tasks_bp.route('/tasks', methods=['GET'])
@login_required
def tasks():
    user_tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('tasks.html', tasks=user_tasks)

@tasks_bp.route('/task/new', methods=['GET', 'POST'])
@login_required
def new_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, description=form.description.data, author=current_user)
        db.session.add(task)
        db.session.commit()
        flash('Your task has been created!', 'success')
        return redirect(url_for('tasks.tasks'))
    return render_template('add_task.html', form=form)

@tasks_bp.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403)
    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        db.session.commit()
        flash('Your task has been updated!', 'success')
        return redirect(url_for('tasks.tasks'))
    elif request.method == 'GET':
        form.title.data = task.title
        form.description.data = task.description
    return render_template('edit_task.html', form=form)

@tasks_bp.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403)
    db.session.delete(task)
    db.session.commit()
    flash('Your task has been deleted!', 'success')
    return redirect(url_for('tasks.tasks'))
