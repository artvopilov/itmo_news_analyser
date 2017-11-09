<head>
  <link href="stylen.css" rel="stylesheet">
</head>
<table border=1 align="center">
    <tr style="background: red;">
        <th>Title</th>
        <th>Author</th>
        <th>#likes</th>
        <th>#comments</th>
        <th colspan="3">Label</th>
    </tr>
    %for row, color in rows:
        <tr style="background-color: {{color}};">
			<td><a class="title transition" href="{{row.url}}" target="_blank">{{row.title}}</a></td>
            <td>{{row.author}}</td>
            <td>{{row.points}}</td>
            <td>{{row.comments}}</td>
            <td><a class="labelg transition" href="/add_label?label=good&id={{row.id}}">Интересно</a></td>
            <td><a class="labely transition" href="/add_label?label=maybe&id={{row.id}}">Возможно</a></td>
            <td><a class="labelb transition" href="/add_label?label=never&id={{row.id}}">Не интересно</a></td>
        </tr>
    %end
</table>
<p align="center"><a href="/update_news">I Wanna more HACKER NEWS!</a></p>