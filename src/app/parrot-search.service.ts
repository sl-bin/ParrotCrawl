import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams, HttpResponse, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';

import { ParrotSearch } from './parrot-search';
import { ParrotReturn } from './parrot-return';

// the http headers that define the content type
const httpOptions = {
  headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
  params: new HttpParams(),
  responseType: 'text' as 'json'
};


@Injectable({ providedIn: 'root' })
export class ParrotSearchService {

  // node route URL to accept search POST request
  private nodeURL = "http://localhost:4220/api/search";

  dataRet: ParrotReturn;
  private testLoaded = new BehaviorSubject('default message');
  loaded = this.testLoaded.asObservable();
  private testSuccess = new BehaviorSubject('default message');
  success = this.testSuccess.asObservable();

  loaded: Boolean;
  success: Boolean;

  constructor(private http: HttpClient) { }

  // from: https://angular.io/guide/http
  private handleError(error: HttpErrorResponse) {
    if (error.error instanceof ErrorEvent) {
      // A client-side or network error occurred. Handle it accordingly.
      console.error('An error occurred:', error.error.message);
    } else {
      // The backend returned an unsuccessful response code.
      // The response body may contain clues as to what went wrong,
      console.error(
        `Backend returned code ${error.status}, ` +
        `body was: ${error.error}`);
    }
    // return an observable with a user-facing error message
    return throwError(
      'An Error occurred. Please try again.');
  };

  // method to recieve search input from form and POST to given URL
   postSearch(search: ParrotSearch): Observable<ParrotSearch> {

    console.log('Here we are in Angular, and the data sent to node is: ' + JSON.stringify(search));
    //and make the post request
    return this.http.post<ParrotSearch>(this.nodeURL, search, httpOptions).pipe(
      catchError(this.handleError)
    // this.dataRet = this.http.post<ParrotSearch>(this.nodeURL, search, httpOptions).pipe(
    //   catchError(this.handleError)
    );
  }
}
