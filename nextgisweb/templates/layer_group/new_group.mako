<%inherit file='../base.mako' />
<%namespace file="util.mako" import="*" />
<%namespace file="../wtforms.mako" import="*" />

${title_block()}

<form method="POST">
    <fieldset>
    ${render_form(form)}
    </fieldset>
</form>