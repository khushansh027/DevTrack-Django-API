import json
import os
from django.http import JsonResponse
from django.conf import settings
from issues.models import Reporter, Issue, CriticalIssue, LowPriorityIssue

REPORTERS_FILE = os.path.join(settings.BASE_DIR, 'reporters.json')
ISSUES_FILE = os.path.join(settings.BASE_DIR, 'issues.json')

def reporters_view(request):
      # Create a new reporter
      if request.method == 'POST':
            try:
                  # load data from request body
                  data = json.loads(request.body)
                  # create a Reporter instance to validate it and 
                  reporter = Reporter(
                        id = data.get('id'),
                        name =  data.get('name'),
                        email = data.get('email'),
                        team = data.get('team')
                  )
                  reporter.validate()              
                  # Save reporter to file and add to reporter object
                  with open(REPORTERS_FILE, 'r') as f:
                        reporters = json.load(f)
                  reporters.append(reporter.to_dict())
                  
                  # write back to file
                  with open(REPORTERS_FILE, 'w') as f:
                        json.dump(reporters, f, indent=2)
                  return JsonResponse(reporter.to_dict(), status=201)
      
            except ValueError as e:
                  return JsonResponse({'error': str(e)}, status=400)
      
      # Read the existing reporters
      elif request.method == 'GET':
            try:
                  # Check if file exists first
                  with open(REPORTERS_FILE, 'r') as f:
                        reporters = json.load(f)
                  
                  reporter_id = request.GET.get('id')
                  
                  # if asked for specific id:
                  if reporter_id:
                        found_reporter = None
                        # Search the list for the reporter with the given id
                        for r in reporters:
                              if str(r['id']) == reporter_id:
                                    found_reporter = r
                                    break
                        if found_reporter:
                              return JsonResponse(found_reporter, status=200)
                        else:
                              return JsonResponse({'error': 'Reporter not found'}, status=404)
                  
                  # if not asked for specific id, return all:
                  else:
                        return JsonResponse(reporters, safe=False, status=200)
            except FileNotFoundError:
                  return JsonResponse([], safe=False, status=200)
            except json.JSONDecodeError:
                  return JsonResponse({'error': 'Database file is corrupted'}, status=500)
            except Exception as e:
                  return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
         
def issues_view(request):
      # Create a new issue
      if request.method == 'POST':
            try:
                  # load data from request body
                  data = json.loads(request.body)
                  # create a Issue instance to validate it 
                  if data['priority'] == 'critical':
                        issue = CriticalIssue(
                              id = data.get('id'),
                              title =  data.get('title'),
                              description = data.get('description'),
                              status = data.get('status'),
                              priority = data.get('priority'),
                              reporter_id = data.get('reporter_id')
                        )
                  elif data['priority'] == 'low':
                        issue = LowPriorityIssue(
                              id = data.get('id'),
                              title =  data.get('title'),
                              description = data.get('description'),
                              status = data.get('status'),
                              priority = data.get('priority'),
                              reporter_id = data.get('reporter_id')
                        )
                  else:
                        issue = Issue(
                              id = data.get('id'),
                              title =  data.get('title'),
                              description = data.get('description'),
                              status = data.get('status'),
                              priority = data.get('priority'),
                              reporter_id = data.get('reporter_id')
                        )
                  issue.validate()
                  # Save issue to file
                  with open(ISSUES_FILE, 'r') as f:
                        issues = json.load(f)
                  issues.append(issue.to_dict())
                  
                  # write back to file
                  with open(ISSUES_FILE, 'w') as f:
                        json.dump(issues, f, indent=2)
                        
                  response_data = issue.to_dict()
                  response_data['message'] = issue.describe()
                  return JsonResponse(response_data, status=201)
                        
            except ValueError as e:
                  return JsonResponse({'error': str(e)}, status=400)
            
      # read the existing issue
      elif request.method == 'GET':
            try:
                  with open(ISSUES_FILE, 'r') as f:
                        issues = json.load(f)
                  issue_id = request.GET.get('id')
                  status_filter = request.GET.get('status')
                  
                  if issue_id:
                        found_issue = None   
                        for i in issues:
                              if str(i['id']) == issue_id:
                                    found_issue = i
                                    break
                        if found_issue:
                              return JsonResponse(found_issue, status=200)
                        else:
                              return JsonResponse({'error': 'Issue not found'}, status=404)
                  
                  elif status_filter:
                        filtered = []
                        for i in issues:
                              if i['status'] == status_filter:
                                    filtered.append(i)
                        return JsonResponse(filtered, safe=False, status=200)                    
                  
                  else:
                        return JsonResponse(issues, safe=False, status=200)
            
            except FileNotFoundError:
                  return JsonResponse([], safe=False, status=200)
            except json.JSONDecodeError:
                  return JsonResponse({'error': 'Database file is corrupted'}, status=500)
            except Exception as e:
                  return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
                  