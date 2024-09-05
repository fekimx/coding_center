//Make a globalMailbox variable and initialize it to inbox
var globalMailbox = 'inbox';

document.addEventListener('DOMContentLoaded', function() {
  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('#send-email').addEventListener('click', send_email)

  // By default, load the inbox 
  load_mailbox('inbox');

});

function compose_email() {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#single-email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

}//end of compose_email

function prefilled_compose_email(sender, subject, date_time, body) {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#single-email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Fill composition fields using parameters
  document.querySelector('#compose-recipients').value = sender;
  // Check if the subject has "Re: " or not
  if(subject.slice(0,4) === "Re: ")
    document.querySelector('#compose-subject').value = subject;
  else 
    document.querySelector('#compose-subject').value = "Re: " + subject;
  document.querySelector('#compose-body').value = "On " + date_time + " " + sender + " wrote:\n"+body+"\n-----\n";

}//end of prefilled_compose_email

function send_email(event){
  // Retrieve values from the form elements
  let recipients = document.querySelector('#compose-recipients').value;
  let subject = document.querySelector('#compose-subject').value;
  let body = document.querySelector('#compose-body').value;

  // Use fetch to make a POST request
  fetch('/emails', {
    method: "POST",
    body: JSON.stringify({
      recipients: recipients, 
      subject: subject,
      body: body
    })
  })
  // Put response into json form
  .then(response => response.json())
  .then(() => {
    load_mailbox('sent');
  });
  event.preventDefault();

}//end of send_email

function load_mailbox(mailbox) {
  globalMailbox = mailbox;

  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    // Check if there are any emails in the mailbox
    if(emails.length === 0) {
      document.querySelector('#emails-view').innerHTML += 'You have no emails.';
    }
    // If there are any emails in the mailbox, show it
    else {
      emails.forEach(add_email_to_view)
    }
  });

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#single-email-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  return false;

}//end of load_mailbox

function add_email_to_view(email) {
  //Create a new element for the email
  const row = document.createElement('div');
  //Add border-bottom and background color gray
  row.classList.add('email');
  //If it is not read, change background to white
  if(!email.read) {
    row.classList.add('unread');
  }

  recipients = `<strong>${email.recipients}</strong>`;
  sender = `<strong>${email.sender}</strong>`;
  subject = `${email.subject}`;
  time = `<span>${email.timestamp}</span>`;
  body = `<pre>${email.body}</pre>`;

  //check which mailbox so either the sender or the recipient is displayed
  if(globalMailbox === 'sent') {
    // I added To: just like in Gmail!
    row.innerHTML = `To:&nbsp;${recipients}&nbsp;&nbsp;&nbsp;&nbsp;${subject} ${time}`;
  }
  else {
    row.innerHTML = `${sender}&nbsp;&nbsp;&nbsp;&nbsp;${subject} ${time}`;
  }

  //If an email is clicked (any of the div elements), then show that email
  row.addEventListener('click', function() {
    show_single_email(email.id);
  })
  document.querySelector('#emails-view').append(row);
  
}//end of add_email_to_view

function show_single_email(email_id) {
  //Show the email that has been clicked on and mark it as read 
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#single-email-view').style.display = 'block';
  
  mark_it_read(email_id);
    
  //Get the email and display with the preset label e.g. Subject: Hi
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
    const recipients = `<br>To:&nbsp;<strong>${email.recipients}</strong>`;
    const sender = `From:&nbsp;<strong>${email.sender}</strong>`;
    const subject = `<br>Subject:&nbsp;${email.subject}`;
    const date_time = `<br>Date:&nbsp;<span style="float:none;">${email.timestamp}</span>`;
    const body = `<pre>${email.body}</pre>`;
    document.querySelector('#single-email-view').innerHTML = `${sender} ${recipients} ${date_time} ${subject}<br><br>${body}`;
    
    // Create Reply button, when clicked call prefilled_compose_email function
    const reply_button = document.createElement('button');
    reply_button.textContent = 'Reply';
    reply_button.addEventListener('click', () => prefilled_compose_email(email.sender, email.subject, email.timestamp, email.body));
    
    const archive_button = document.createElement('button');
    // If inbox is loaded, change text to Archive and make archive property true, do the opposite in else
    /** I got help from Vlad to do this part! **/
    if(globalMailbox === 'inbox') {
      archive_button.textContent = 'Archive';      
      archive_button.addEventListener('click', () => archive(email_id, true));
    }
    else if(globalMailbox === 'archive') {
      archive_button.textContent = 'Unarchive';
      archive_button.addEventListener('click', () => archive(email_id, false));
    }
    // Add both buttons to the view
    document.querySelector('#single-email-view').append(reply_button);
    document.querySelector('#single-email-view').append(archive_button);
  });
}

function mark_it_read(email_id) {
  fetch(`/emails/${email_id}`, {
    method: "PUT",
    body: JSON.stringify({
      read: true
    })
  })
}

function archive(email_id, to_archive){
  fetch(`/emails/${email_id}`, {
    method: "PUT",
    body: JSON.stringify({
      archived: to_archive
    })
  })
  .then(() => {
    load_mailbox('inbox');
  })
}

// function unarchive(email_id){
//   unarchive_button = `<br><input type="submit" id="unarchive_button" value="Unarchive">`;
//   document.querySelector('#single-email-view').innerHTML += `${unarchive_button}`; 
//   document.querySelector('#unarchive_button').addEventListener('click', function() {
//     fetch(`/emails/${email_id}`, {
//       method: "PUT",
//       body: JSON.stringify({
//         archived: false
//       })
//     })
//   })
// }

//DIDN'T WORK THIS WAY
// reply_button = `<br><input type="submit" id="reply_button" value="Reply">`;
// document.querySelector('#single-email-view').innerHTML += `${reply_button}`;
// document.querySelector('#reply_button').addEventListener('click', () => prefilled_compose_email(email.sender, email.subject, email.timestamp, email.body));
    